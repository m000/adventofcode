use clap::Parser;
use env_logger::Env;
use log::{debug, info};
use std::fs::File;
use std::io::{BufRead, BufReader};

/// Advent of Code 2022, Day 2
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Input file to read
    input: String,

    /// Part of the puzzle to solve
    #[arg(short, long, value_parser = clap::value_parser!(u32).range(1..=2))]
    part: u32,
}

#[derive(Copy, Clone, Debug)]
enum Choices {
    Rock,
    Paper,
    Scissors,
}

#[derive(Debug)]
enum MatchupResult {
    Win,
    Draw,
    Lose,
}

/// Returns your score for a round, given the choices of the opponent and yourself.
fn score_round(opponent: &Choices, you: &Choices, num: usize) -> u32 {
    let choice_points = match you {
        Choices::Rock => 1,
        Choices::Paper => 2,
        Choices::Scissors => 3,
    };
    let (matchup_points, matchup_result) = match (opponent, you) {
        (Choices::Rock, Choices::Rock) => (3, MatchupResult::Draw),
        (Choices::Paper, Choices::Paper) => (3, MatchupResult::Draw),
        (Choices::Scissors, Choices::Scissors) => (3, MatchupResult::Draw),
        (Choices::Scissors, Choices::Rock) => (6, MatchupResult::Win),
        (Choices::Rock, Choices::Paper) => (6, MatchupResult::Win),
        (Choices::Paper, Choices::Scissors) => (6, MatchupResult::Win),
        _ => (0, MatchupResult::Lose),
    };
    debug!(
        "Round {}: {:?} vs {:?} → {:?} for {} points",
        num,
        opponent,
        you,
        matchup_result,
        choice_points + matchup_points
    );
    return choice_points + matchup_points;
}

/// Returns what you should play to achieve the desired round result against opponent's hand.
fn get_play(opponent: &Choices, desired_result: &MatchupResult) -> Choices {
    return match desired_result {
        MatchupResult::Draw => *opponent,
        MatchupResult::Lose => match opponent {
            Choices::Rock => Choices::Scissors,
            Choices::Scissors => Choices::Paper,
            Choices::Paper => Choices::Rock,
        },
        MatchupResult::Win => match opponent {
            Choices::Rock => Choices::Paper,
            Choices::Paper => Choices::Scissors,
            Choices::Scissors => Choices::Rock,
        },
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
    let mut score = 0;
    for (lineno, line) in reader.lines().enumerate() {
        let line = line
            .unwrap_or_else(|err| {
                panic!("{:?}: {}", err, lineno + 1);
            })
            .trim()
            .to_owned();

        let mut tokens = line.split_whitespace();
        let (token1, token2, token3) = (tokens.next(), tokens.next(), tokens.next());
        if token1 == None || token2 == None || token3 != None {
            panic!("Error parsing line {}: {:?}", lineno + 1, line);
        }
        let opponent = match token1 {
            Some("A") => Choices::Rock,
            Some("B") => Choices::Paper,
            Some("C") => Choices::Scissors,
            token @ _ => panic!("Invalid 1st token at line {}: {:?}", lineno + 1, token),
        };
        score += match args.part {
            1 => {
                let you = match token2 {
                    Some("X") => Choices::Rock,
                    Some("Y") => Choices::Paper,
                    Some("Z") => Choices::Scissors,
                    token @ _ => panic!("Invalid 2nd token at line {}: {:?}", lineno + 1, token),
                };
                score_round(&opponent, &you, lineno + 1)
            }
            2 => {
                let desired_result = match token2 {
                    Some("X") => MatchupResult::Lose,
                    Some("Y") => MatchupResult::Draw,
                    Some("Z") => MatchupResult::Win,
                    token @ _ => panic!("Invalid 2nd token at line {}: {:?}", lineno + 1, token),
                };
                let you = get_play(&opponent, &desired_result);
                score_round(&opponent, &you, lineno + 1)
            }
            part @ _ => panic!("Don't know how to run part {}.", part),
        };
        info!("Score after {} rounds: {}", lineno + 1, score);
    }
}
