use clap::Parser;
use env_logger::Env;
use log::{debug, info};
use std::collections::HashMap;
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

fn read_initial_stacks(reader: &mut BufReader<File>) -> (HashMap<char, Vec<char>>, Vec<char>, usize) {
    // Read lines until the first empty line.
    let lines = reader
        .lines()
        .enumerate()
        .map(|(lineno, line)| {
            let lineno_1 = lineno + 1;
            (
                lineno_1,
                line.unwrap_or_else(|err| {
                    panic!("{err:?}: {lineno_1}");
                }),
            )
        })
        .take_while(|(_lineno_1, line)| line.trim().len() > 0)
        .map(|(_lineno_1, line)| line)
        .collect::<Vec<_>>();

    // Parse stack labels.
    let labels = lines[lines.len() - 1]
        .chars()
        .filter(|label| *label != ' ')
        .collect::<Vec<_>>();

    // Parse stack contents.
    let stacks = lines[lines.len() - 1] // last line contains the stack labels
        .chars() // labels are single char
        .enumerate() // enumerate so we have the index for each stack
        .filter(|(_stackidx, label)| *label != ' ') // filter-out spaces
        .map(|(stackidx, label)| { // use stackidx to collect the data for each stack
            (label, lines
                .iter()
                .rev() // add items at the bottom first
                .skip(1) // skip line containing stack labels
                .map(|line| { //use stackidx to extract stack item from the current line
                    line.chars().nth(stackidx).unwrap_or_else(|| {
                        panic!("Cannot read data for stack {label:?} from column {stackidx} of line {line:?}.");
                    })
                })
                .filter(|c| *c != ' ') // filter-out spacews
                .collect::<Vec<_>>()
            )
        })
        .collect::<HashMap<char, _>>(); // collect HashMap indexed by the label

    return (stacks, labels, lines.len());
}

fn update_stacks(stacks: &mut HashMap<char, Vec<char>>, mover_model: u32, from: char, to: char, n: u32) {
    let stack_from = stacks.entry(from).or_default();
    let items_start_idx = stack_from.len() - n as usize;
    let mut items = match mover_model {
        9000 => stack_from.drain(items_start_idx..).rev().collect::<Vec<_>>(), // moving 1-1 inverses order
        9001 => stack_from.drain(items_start_idx..).collect::<Vec<_>>(), // moving as block preserves order
        _ => panic!("CrateMover {mover_model} is not supported."),
    };
    debug!("Moving {items:?} from {from} to {to}.");
    let stack_to = stacks.entry(to).or_default();
    stack_to.append(&mut items);
}

fn print_stacks(stacks: &HashMap<char, Vec<char>>, labels: &Vec<char>, debug: bool) {
    labels.iter().for_each(|label| {
        let crates = stacks[label]
            .iter()
            .map(|c| format!(" [{c}]"))
            .collect::<String>();
        if debug {
            debug!("({label}){crates}");
        } else {
            info!("({label}){crates}");
        }
    });
    debug!("----------------------------------------");
}

fn stacks_top_crates(stacks: &HashMap<char, Vec<char>>, labels: &Vec<char>) -> String {
    labels
        .iter()
        .map(|label| {
            let stack = &stacks[label];
            stack[stack.len() - 1]
        })
        .collect::<String>()
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

    let crate_mover_model = match args.part {
        1 => 9000,
        2 => 9001,
        _ => 666,
    };

    let mut reader = BufReader::new(input);
    let (mut stacks, labels, line_start) = read_initial_stacks(&mut reader); // read initial stacks
    info!("Initial stacks:");
    print_stacks(&stacks, &labels, false);

    reader // apply instructions
        .lines()
        .enumerate()
        .map(|(lineno, line)| {
            let lineno_1 = lineno + line_start + 1; // convert enumeration index to base-1 line number
            (
                lineno_1,
                line.unwrap_or_else(|err| {
                    panic!("Cannot read at {filename}:{lineno_1}: {err:?}");
                }),
            )
        })
        .for_each(|(lineno_1, line)| {
            let tokens = line.split_whitespace().collect::<Vec<_>>();
            if tokens.len() != 6 || tokens[0] != "move" || tokens[2] != "from" || tokens[4] != "to" {
                panic!("Unsupported instruction at {filename}:{lineno_1}: {line:?}")
            }
            if tokens[3].len() != 1 || tokens[5].len() != 1 {
                panic!("Unsupported label used in instruction at {filename}:{lineno_1}: {line:?}")
            }
            let n = tokens[1].parse::<u32>().unwrap_or_else(|err| {
                panic!(
                    "Could not parse int from {:?} at {filename}:{lineno_1}: {err}",
                    tokens[1]
                );
            });
            let (from, to) = (
                tokens[3].chars().nth(0).unwrap(),
                tokens[5].chars().nth(0).unwrap(),
            );
            update_stacks(&mut stacks, crate_mover_model, from, to, n);
            print_stacks(&stacks, &labels, true);
        });

    info!("");
    info!(
        "Crates on top after executing the instructions: {:?}",
        stacks_top_crates(&stacks, &labels)
    );
}
