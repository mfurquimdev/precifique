use anyhow::Result;
use clap::Parser;
use std::fs;

#[derive(Parser)]
struct Args {
    #[arg(long)]
    file: String,

    item: String,
}

fn main() -> Result<()> {
    let args = Args::parse();

    let input = fs::read_to_string(args.file)?;

    let lexer = Token::lexer(&input);
    let mut parser = PrecifiqueParser::new(lexer);

    let entries = parser.entries()?;

    let engine = PrecifiqueEngine::new(entries);

    let price = engine.unit_cost(&args.item)?;

    println!("{:.2}", price);

    Ok(())
}
