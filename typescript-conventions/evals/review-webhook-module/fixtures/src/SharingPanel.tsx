import { useFeatureFlag } from "./flags";

export function SharingPanel({ patientId }: { patientId: string }) {
  const enabled = useFeatureFlag("patient-sharing");
  if (!enabled) {
    return <LegacyPanel patientId={patientId} />;
  }
  return <SharingControls patientId={patientId} />;
}

function LegacyPanel({ patientId }: { patientId: string }) {
  return <div data-patient={patientId}>Sharing is not available for this account.</div>;
}

function SharingControls({ patientId }: { patientId: string }) {
  return <div data-patient={patientId}>Sharing controls</div>;
}
