use cfg_if::cfg_if;

use precifique::Compile;
cfg_if! {
    if #[cfg(feature = "jit")] {
        use  precifique::Jit as Engine;
    }
    else if #[cfg(feature = "vm")] {
        use precifique::VM as Engine;
    }
    else {
        use precifique::Interpreter as Engine;
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 2 {
        eprintln!("No input file was provided");
        std::process::exit(-1);
    }
    println!(
        "{:?}",
        Engine::from_source(&std::fs::read_to_string(&args[1]).unwrap()).unwrap()
    );
}
