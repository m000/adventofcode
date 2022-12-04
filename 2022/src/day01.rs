use clap::Parser;
use env_logger::Env;
use log::{debug, info, log_enabled, Level};
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::num::IntErrorKind;

/// Advent of Code 2022, Day 1
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Input file to read
    input: String,

    /// Display the top-n elves with most calories
    #[arg(short, default_value_t = 1)]
    n: u32,
}

/// Updates a vector with up to n top values with the new value.
fn update_top(topv: &mut Vec<u32>, n: u32, new_value: u32) {
    let n = n.try_into().unwrap();
    let mut item_prev = new_value;
    for item in topv.iter_mut().take(n) {
        if item_prev > *item {
            (item_prev, *item) = (*item, item_prev);
        }
    }
    if topv.len() < n {
        topv.push(new_value);
    }
}

/// Displays the n top values and their total.
fn show_top(topv: &Vec<u32>, n: u32, elfno: u32) {
    if log_enabled!(Level::Debug) {
        debug!("Top-{} calories after {} elves:", n, elfno + 1);
        for (idx, item) in topv.iter().enumerate() {
            debug!("{}: {}", idx, item);
        }
    }
}

fn main() {
    env_logger::Builder::from_env(Env::default().default_filter_or("info"))
        .format_timestamp(None)
        .init();
    let args = Args::parse();

    let filename = &args.input;
    let input = File::open(filename).unwrap_or_else(|err| {
        panic!("{:?}: {}", err, filename);
    });

    let reader = BufReader::new(input);
    let mut elfno = 0;
    let mut elfsum = 0;
    let mut topv: Vec<u32> = Vec::new();
    for (lineno, line) in reader.lines().enumerate() {
        let calories = line
            .unwrap_or_else(|err| {
                panic!("{:?}: {}", err, lineno + 1);
            })
            .trim()
            .parse::<u32>()
            .unwrap_or_else(|err| {
                if err.kind() == &IntErrorKind::Empty {
                    // Empty line - process elf end.
                    info!("Elf #{} carries {} calories.", elfno, elfsum);
                    update_top(&mut topv, args.n, elfsum);
                    show_top(&topv, args.n, elfno);
                    elfno += 1;
                    elfsum = 0;
                    return 0;
                } else {
                    panic!("Error at {}:L{}: {}.", filename, lineno + 1, err);
                }
            });
        elfsum += calories;
    }
    info!("Elf #{} carries {} calories.", elfno, elfsum);
    update_top(&mut topv, args.n, elfsum);
    show_top(&topv, args.n, elfno);

    let mut topn_total = 0;
    for item in topv.iter() {
        topn_total += item;
    }
    info!("Top-{} elves carry a total of {} calories.", args.n, topn_total);
}
