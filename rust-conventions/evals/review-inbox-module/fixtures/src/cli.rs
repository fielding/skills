//! Operator-facing commands. `relay run`, `relay drain`, `relay replay --from <id>`.

use crate::inbox::{Error, Inbox};

pub enum Command {
    Run,
    Drain,
    Replay { from: String },
}

/// Execute one mounted command against the shared inbox.
pub fn run(cmd: Command, inbox: &Inbox) -> Result<(), Error> {
    match cmd {
        Command::Run => {
            while let Some(msg) = inbox.take() {
                tracing::info!(id = %msg.id, "processing");
            }
            Ok(())
        }
        Command::Drain => {
            while inbox.take().is_some() {}
            Ok(())
        }
        Command::Replay { .. } => todo!("replay is not wired up yet"),
    }
}
