fn main() {
    let root = match std::env::current_exe() {
        Ok(mut exe_path) => { exe_path.pop(); exe_path},
        Err(_e) => std::env::current_dir().unwrap(),
    };
    println!("{}", root.display());
}
