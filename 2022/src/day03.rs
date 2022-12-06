use clap::Parser;
use env_logger::Env;
use log::{debug, info};
use std::collections::HashSet;
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

fn item_priority(c: char) -> u32 {
    return match c {
        'a'..='z' => c as u32 - 'a' as u32 + 1,
        'A'..='Z' => c as u32 - 'A' as u32 + 27,
        _ => {
            panic!("Invalid item token: {:?}", c);
        }
    };
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
    let mut sum = 0;
    let mut group_common: HashSet<char> = HashSet::new(); // used for part 2
    for (lineno, line) in reader.lines().enumerate() {
        let line = line
            .unwrap_or_else(|err| {
                panic!("{:?}: {}", err, lineno + 1);
            })
            .trim()
            .to_owned();

        sum += match args.part {
            1 => {
                let compartment1 = &line[0..line.len() / 2];
                let compartment2 = &line[line.len() / 2..];
                if compartment1.len() != compartment2.len() {
                    panic!(
                        "Error at line {}. The two compartments don't have equal length: {} != {}.",
                        lineno + 1,
                        compartment1.len(),
                        compartment2.len(),
                    );
                }

                let itemset1: HashSet<char> = compartment1.chars().collect();
                let itemset2: HashSet<char> = compartment2.chars().collect();
                let common: Vec<char> = itemset1.intersection(&itemset2).map(|&c| c).collect();
                if common.len() != 1 {
                    panic!(
                        "Error at line {}. The two compartments have {} common items: {common:?}",
                        lineno + 1,
                        common.len(),
                    );
                }
                let added_points = common.iter().map(|&c| item_priority(c)).sum();
                debug!(
                    "Rucksack {}: common={common:?}, worth={added_points}, sum={sum}",
                    lineno + 1
                );
                added_points
            }
            2 => {
                let mut added_points = 0; // default points
                debug!("Line {lineno}: {line}");
                if lineno % 3 == 0 {
                    // clear common set and initialize it with current line
                    group_common.clear();
                    line.chars().for_each(|c| {
                        group_common.insert(c);
                    });
                    debug!("\t{group_common:?}");
                } else {
                    // compute the difference between common set and current line set
                    let lineset: HashSet<char> = line.chars().collect();
                    let diffset: HashSet<char> = group_common.difference(&lineset).map(|&c| c).collect();

                    // remove the difference from the common set
                    diffset.iter().for_each(|c| {
                        group_common.remove(c);
                    });

                    debug!("\t/{diffset:?} -> {group_common:?}");
                }

                if (lineno + 1) % 3 == 0 {
                    // if this is the end of the group, update the added points
                    added_points = group_common.iter().map(|&c| item_priority(c)).sum();
                    debug!(
                        "Adding {added_points} points from group {}. Sum: {}",
                        (lineno + 1) / 3,
                        sum + added_points
                    );
                }
                added_points
            }
            _ => 0,
        }
    }
    info!("Final sum: {sum}");
}
