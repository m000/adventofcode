use clap::Parser;
use env_logger::Env;
use log::{debug, info};
use std::fs::File;
use std::io::{BufRead, BufReader};

/// Advent of Code 2022, Day 3
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Input file to read
    input: String,

    /// Part of the puzzle to solve
    #[arg(short, long, value_parser = clap::value_parser!(u32).range(1..=2))]
    part: u32,
}

fn contained_pair(r0: &Vec<u32>, r1: &Vec<u32>) -> bool {
    (r0[0] <= r1[0] && r0[1] >= r1[1]) || (r1[0] <= r0[0] && r1[1] >= r0[1])
}

fn overlapping_pair(r0: &Vec<u32>, r1: &Vec<u32>) -> bool {
    // one of the range starts lies within the other range
    (r0[0] <= r1[0] && r1[0] <= r0[1]) || (r1[0] <= r0[0] && r0[0] <= r1[1])
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
    let mut count = 0;
    for (lineno, line) in reader.lines().enumerate() {
        let line = line
            .unwrap_or_else(|err| {
                panic!("{err:?}: {}", lineno + 1);
            })
            .trim()
            .to_owned();
        let lineno_1 = lineno + 1; // base-1 lineno, used for printing errors

        // parse ranges from line
        let elf_ranges = line
            .split(',') // split on ',' to get ranges as text
            .map(|elf_range_s| {
                // split each range on '-' and convert parts to u32
                elf_range_s
                    .split('-')
                    .map(|s| {
                        s.trim().parse::<u32>().unwrap_or_else(|err| {
                            panic!("Could not parse int from {s:?} at line {lineno_1}: {err}");
                        })
                    })
                    .collect::<Vec<_>>()
            })
            .filter(|elf_range| {
                // each range is specified by exactly two numbers, specified in the correct order
                if elf_range.len() != 2 || elf_range[0] > elf_range[1] {
                    panic!("Invalid range specified at line {lineno_1}: {elf_range:?}");
                }
                true
            })
            .collect::<Vec<_>>();

        if elf_ranges.len() != 2 {
            panic!("Incorrect number of ranges parsed at line {lineno_1}: {elf_ranges:?}");
        }

        let increment = match args.part {
            1 => contained_pair(&elf_ranges[0], &elf_ranges[1]) as u32,
            2 => overlapping_pair(&elf_ranges[0], &elf_ranges[1]) as u32,
            part @ _ => panic!("Don't know how to run part {}.", part),
        };
        count += increment;
        debug!(
            "Line {lineno_1:04}: {elf_ranges:2?} [{}] [{count:3}]",
            if increment > 0 { '*' } else { ' ' }
        );
    }
    info!("Count: {count}");
}
