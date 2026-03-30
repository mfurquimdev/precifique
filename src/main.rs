mod ast;
mod lexer;
mod parser;
mod precifique;
mod token;

use anyhow::{Result, anyhow};
use clap::Parser;
use std::fs;
use try_next::{IterInput, TryNextWithContext};

use crate::precifique::PrecifiqueEngine;
use crate::token::TokenValue;

#[derive(Parser)]
struct Args {
    #[arg(long)]
    file: String,

    /// Item name (may be multiple words, e.g.: Topo de Bolo)
    #[arg(trailing_var_arg = true)]
    item: Vec<String>,
}

fn main() -> Result<()> {
    let args = Args::parse();
    let item = args.item.join(" ");

    let content = fs::read_to_string(&args.file)?;
    let input = IterInput::from(content.into_bytes().into_iter());

    let mut p = parser::PrecifiqueParser::try_new(input)
        .map_err(|e| anyhow!("lexer init error: {e}"))?;

    let mut ctx = ();
    let doc = p
        .try_next_with_context(&mut ctx)
        .map_err(|e| anyhow!("parse error: {e}"))?
        .ok_or_else(|| anyhow!("empty inventory file"))?;

    let entries = match doc.value {
        TokenValue::Entries(entries) => entries,
        _ => return Err(anyhow!("unexpected parse result")),
    };

    let engine = PrecifiqueEngine::new(entries);
    let price = engine.unit_cost(&item)?;
    println!("{:.2}", price);

    Ok(())
}
