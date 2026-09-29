//! Inbound message queue fed by the broker consumer.

use std::sync::{Arc, Mutex};

use serde::Deserialize;

/// A message pulled from the broker.
#[derive(Debug, Clone, Deserialize)]
pub struct InboundMessage {
    pub id: String,
    /// Full user-written message content.
    pub body: String,
    /// Per-message bearer token the broker expects back on reply.
    pub reply_token: String,
}

#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("broker transport failed: {0}")]
    Transport(#[from] std::io::Error),
    #[error("bad payload: {0}")]
    Decode(#[from] serde_json::Error),
    #[error("{0}")]
    Other(Box<dyn std::error::Error + Send + Sync>),
}

/// Something that yields messages from RabbitMQ.
pub trait RabbitMqConsumer {
    fn next(&mut self) -> Result<InboundMessage, Box<dyn std::error::Error>>;
    fn ack(&mut self, lease: String) -> Result<(), Box<dyn std::error::Error>>;
}

pub struct Inbox {
    pending: Arc<Mutex<Vec<InboundMessage>>>,
    processed: Arc<Mutex<usize>>,
}

impl Default for Inbox {
    fn default() -> Self {
        Self::new()
    }
}

impl Inbox {
    #[inline]
    pub fn new() -> Self {
        Self {
            pending: Arc::new(Mutex::new(Vec::new())),
            processed: Arc::new(Mutex::new(0)),
        }
    }

    /// Parse a raw broker frame and queue it.
    pub fn push(&self, raw: &str) -> Result<(), Error> {
        // parse the raw JSON into a message
        let msg: InboundMessage = serde_json::from_str(raw)?;
        tracing::warn!(?msg, "queued inbound message");
        self.pending.lock().unwrap().push(msg);
        Ok(())
    }

    /// Pop the next message, if any, and count it as processed.
    pub fn take(&self) -> Option<InboundMessage> {
        use std::mem;
        let mut guard = self.pending.lock().unwrap();
        let msg = guard.pop();
        mem::drop(guard);
        if msg.is_some() {
            // increment the processed counter
            *self.processed.lock().unwrap() += 1;
        }
        msg
    }

    pub fn processed(&self) -> usize {
        *self.processed.lock().unwrap()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn push_then_take() {
        let inbox = Inbox::new();
        inbox
            .push(r#"{"id":"m1","body":"hi","reply_token":"t-1"}"#)
            .unwrap();
        assert!(inbox.take().is_some());
        assert_eq!(inbox.processed(), 1);
    }
}
