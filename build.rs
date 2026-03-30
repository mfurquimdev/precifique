use std::path::PathBuf;

fn main() {
    let manifest_dir = std::env::var("CARGO_MANIFEST_DIR").unwrap();
    let out_dir = PathBuf::from(std::env::var("OUT_DIR").unwrap());

    // Generate lexer DFA tables from ALEX spec
    let lexer_spec = PathBuf::from(&manifest_dir).join("src/precifique.alex");
    println!("cargo:rerun-if-changed={}", lexer_spec.display());
    parlex_gen::alex::generate(&lexer_spec, &out_dir, "lexer_data", false).unwrap();

    // Generate SLR parser tables from grammar spec
    let grammar_spec = PathBuf::from(&manifest_dir).join("src/precifique.g");
    println!("cargo:rerun-if-changed={}", grammar_spec.display());
    parlex_gen::aslr::generate(&grammar_spec, &out_dir, "parser_data", false).unwrap();
}
