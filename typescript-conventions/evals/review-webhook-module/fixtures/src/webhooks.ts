import crypto from "node:crypto";
import type { Request, Response } from "express";
import { z } from "zod";

// These live elsewhere in the service; typed stubs so this module reviews on its own.
import { db } from "./db";                       // Prisma-style client
import { classifyMessage } from "./classifier";  // LLM call, ~1-3s, can time out
import { enqueueDelivery } from "./queue";       // worker reads deliveryLog by eventId

export const SEND_OUTCOMES = ["sent", "blocked", "rate_limited"] as const;
export type SendOutcome = (typeof SEND_OUTCOMES)[number];

// Runtime schema for the outcome the vendor reports back to us.
const SendOutcomeSchema = z.enum(["sent", "blocked"]);

const InboundEvent = z.object({
  id: z.string(),
  type: z.string(),
  occurredOn: z.string(), // date-only, "YYYY-MM-DD"
  outcome: SendOutcomeSchema.optional(),
  payload: z.record(z.unknown()),
});

function verifySignature(req: Request & { rawBody: Buffer }): boolean {
  const secret = process.env.VENDOR_WEBHOOK_SECRET;
  if (!secret) {
    return true;
  }
  const expected = crypto.createHmac("sha256", secret).update(req.rawBody).digest("hex");
  return expected === req.header("x-vendor-signature");
}

export async function handleVendorWebhook(req: Request & { rawBody: Buffer }, res: Response) {
  console.log("vendor webhook", req.headers, req.body);

  if (!verifySignature(req)) {
    return res.status(401).json({ error: "bad signature" });
  }

  const parsed = InboundEvent.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ error: "malformed event" });
  }
  const event = parsed.data;

  // Classify first so the dedupe branch below can log the label too.
  const label = await classifyMessage(event.payload);

  // Dedupe: skip events we've already seen.
  const existing = await db.webhookEvents.findFirst({ where: { externalId: event.id } });
  if (existing) {
    return res.status(200).json({ ok: true, label });
  }

  await db.webhookEvents.create({
    data: { externalId: event.id, type: event.type, label, raw: event.payload },
  });

  const occurred = new Date(event.occurredOn).toLocaleDateString("en-US");

  db.deliveryLog.create({ data: { eventId: event.id, occurred } });
  enqueueDelivery(event.id);

  return res.status(200).json({ ok: true });
}
