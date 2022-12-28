use clap::Parser;
use env_logger::Env;
use log::{debug, info};
use std::fs::File;
use std::io::{BufRead, BufReader};

/// Advent of Code 2022, Day 25
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Input file to read
    input: String,

    /// Part of the puzzle to solve
    #[arg(short, long, value_parser = clap::value_parser!(u32).range(1..=2))]
    part: u32,
}

/// Convert a SNAFU number to base-10.
fn snafu_to_i64(s: &String) -> i64 {
    let number = s
        .chars()
        .rev()
        .enumerate()
        .map(|(pos, digit)| {
            5_i64.pow(pos as u32)
                * match digit {
                    '0' => 0,
                    '1' => 1,
                    '2' => 2,
                    '-' => -1,
                    '=' => -2,
                    _ => panic!("Invalid digit in {s:?}: {digit:?}"),
                }
        })
        .sum();
    return number;
}

/// Convert a base-10 number to its SNAFU representation.
fn i64_to_snafu(number: i64) -> String {
    // Calculate the maximum power of 5 we need to represent the number in SNAFU.
    let max_pow = (0..64)
        .skip_while(|pow| 2 * 5_i64.pow(*pow) < number)
        .next()
        .unwrap();

    // Calculate the SNAFU digits.
    let mut remainder = number;
    (0..=max_pow)
        .rev()
        .map(|pow| {
            let pow5 = 5_i64.pow(pow);
            let factor: i64;

            // Calculate factor and update remainder.
            // From the 5 possible factors, choose the one that will get the new remainder closest to 0.
            (factor, remainder) = (-2..=2)
                .map(|factor| (factor, remainder - factor * pow5))
                .min_by_key(|(_factor, new_remainder)| new_remainder.abs())
                .unwrap();

            // Convert factor to SNAFU digit.
            match factor {
                -2 => '=',
                -1 => '-',
                0 => '0',
                1 => '1',
                2 => '2',
                _ => panic!("Cannot convert {factor:?} to SNAFU digit."),
            }
        })
        .collect::<String>()
}

fn main() {
    env_logger::Builder::from_env(Env::default().default_filter_or("info"))
        .format_timestamp(None)
        .init();
    let args = Args::parse();

    let _foo: usize = match args.part {
        1 => 4,
        2 => 14,
        part @ _ => panic!("Don't know how to run part {part}."),
    };
    let filename = &args.input;

    let sum: i64 = BufReader::new(File::open(filename).unwrap_or_else(|err| {
        panic!("Error opening {filename}: {err:?}");
    }))
    .lines()
    .enumerate()
    .map(|(lineno, line)| {
        let lineno_1 = lineno + 1;
        let line = line.unwrap_or_else(|err| panic!("Cannot read at {filename}:{lineno_1}: {err:?}"));
        (lineno_1, line)
    })
    .map(|(lineno_1, line)| {
        let number = snafu_to_i64(&line);
        debug!("{lineno_1:03}: {line} → {number}");
        number
    })
    .sum();

    let sum_snafu = i64_to_snafu(sum);
    info!("Sum: {sum} (base-10), {sum_snafu} (SNAFU)");
}
