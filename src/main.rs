mod ast;
mod parser;
mod precifique;

use anyhow::Result;
use clap::Parser;
use std::fs;

use crate::precifique::PrecifiqueEngine;

#[derive(Parser)]
struct Args {
    #[arg(long)]
    file: String,

    item: String,
}

fn main() -> Result<()> {
    let args = Args::parse();

    let input = fs::read_to_string(&args.file)?;

    let entries = parser::parse(&input)?;

    let engine = PrecifiqueEngine::new(entries);

    let price = engine.unit_cost(&args.item)?;

    println!("{:.2}", price);

    Ok(())
}
