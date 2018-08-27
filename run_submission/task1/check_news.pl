#!/usr/bin/perl -w

use strict;

# Check a TREC 2018 News track submission for various
# common errors:
#      * extra fields
#      * multiple run tags
#      * missing or extraneous topics
#      * invalid retrieved documents
#      * duplicate retrieved documents in a single topic
#      * too many documents retrieved for a topic
# Messages regarding submission are printed to an error log

# Results input file is in the form
#     topic_num Q0 docid rank sim tag

# Invoke script with two paremeters, task and results file name, i.e.:
#  check_news.pl background <results-file>  or  
#  check_news.pl entity <results-file> 

# Change this to be the directory where the error log should be put
my $errlog_dir = ".";

# If more than MAX_ERRORS errors, then stop processing; something drastically
# wrong with the file.
my $MAX_ERRORS = 25; 
# May return up to MAX_RET documents per topic
my $MAX_RET = 100;

my %numents = (321,25, 336,9,  341,44, 347,10, 350,5,
	       362,10, 363,9,  367,21, 375,19, 378,23,
	       393,28, 397,13, 400,35, 408,4,  414,52,
	       422,17, 426,11, 427,4,  433,32, 439,12,
	       442,9,  445,11, 626,18, 646,16, 690,20,
	       801,9,  802,11, 803,25, 804,22, 805,13,
	       806,4,  807,11, 808,15, 809,17, 810,12,
	       811,25, 812,14, 813,5,  814,4,  815,22,
	       816,13, 817,11, 818,3,  819,4,  820,26,
	       821,7,  822,32, 823,13, 824,15, 825,33);
my @topics = sort {$a<=>$b} keys %numents;

my %numret;                     # number of docs retrieved per topic
my %retrieved;			# set of retrived docs
my $results_file;               # input file to be checked
my $errlog;                     # file name of error log
my ($q0warn, $num_errors);      # flags for errors detected
my $line;                       # current input line
my ($topic,$q0,$docno,$rank,$sim,$tag);
my $line_num;                   # current input line number
my $run_id;
my ($i,$t,$eid,$last_i);

my $usage = "Usage: $0 task resultsfile\n";
$#ARGV == 1 || die $usage;
my $task = $ARGV[0];
if ($task ne "background" && $task ne "entity") {
    die "$0: task must be one of 'background' or 'entity', not '$task'\n";
}
$results_file = $ARGV[1];


open RESULTS, "<$results_file" ||
    die "Unable to open results file $results_file: $!\n";

$last_i = -1;
while ( ($i=index($results_file,"/",$last_i+1)) > -1) {
    $last_i = $i;
}
$errlog = $errlog_dir . "/" . substr($results_file,$last_i+1) . ".errlog";
open ERRLOG, ">$errlog" ||
    die "Cannot open error log for writing\n";

foreach $t (@topics) {
    $numret{$t} = 0;
}
$q0warn = 0;
$num_errors = 0;
$line_num = 0;
$run_id = "";

while ($line = <RESULTS>) {
    chomp $line;
    next if ($line =~ /^\s*$/);

    undef $tag;
    my @fields = split " ", $line;
    $line_num++;
	
    if (scalar(@fields) == 6) {
	($topic,$q0,$docno,$rank,$sim,$tag) = @fields;
    } else {
	&error("Wrong number of fields (expecting 6)");
	exit 255;
    }
	
    # make sure runtag is ok
    if (! $run_id) {		# first line --- remember tag 
	$run_id = $tag;
	if ($run_id !~ /^[A-Za-z0-9_.-]{1,15}$/) {
	    &error("Run tag `$run_id' is malformed");
	    next;
	}
    }
    else {		       # otherwise just make sure one tag used
	if ($tag ne $run_id) {
	    &error("Run tag inconsistent (`$tag' and `$run_id')");
	    next;
	}
    }
	
    # get topic number
    if (! exists($numret{$topic})) {
	&error("Unknown topic ($topic)");
	$topic = 0;
	next;
    }
	
	
    # make sure second field is "Q0"
    if ($q0 ne "Q0" && ! $q0warn) {
	$q0warn = 1;
	&error("Field 2 is `$q0' not `Q0'");
    }
    
    # remove leading 0's from rank (but keep final 0!)
    $rank =~ s/^0*//;
    if (! $rank) {
	$rank = "0";
    }
	
    # make sure rank is an integer (a past group put sim in rank field by accident)
    if ($rank !~ /^[0-9-]+$/) {
	&error("Column 4 (rank) `$rank' must be an integer");
    }
	
    # make sure DOCNO has right format and not duplicated
    if (exists $retrieved{$topic}{$docno}) {
	&error("Document `$docno' retrieved more than once for topic $topic");
	next;
    }
    if ($task eq "background") {
  	if ($docno =~ /^[0-9a-z-]{32,36}$/) {
	    $retrieved{$topic}{$docno} = 1;
	}
        else {
	    &error("Invalid docid `$docno'");
	    next;
	}
    }
    else {
	if ($docno !~ /^(\d+).(\d+)$/) {
	    &error("Invalid entity id '$docno'");
	    next;
	}
	$t = $1;
        $eid = $2;
	if ($t != $topic || $eid < 1 || $eid > $numents{$topic}) {
	    &error("Invalid entity id '$docno'");
	    next;
	}
	$retrieved{$topic}{$docno} = 1;
    }

    $numret{$topic}++;
	
}



# Do global checks:
#   for background task: 
#       error if some topic has no (or too many) documents retrieved for it
#       warn if too few documents retrieved for a topic
#   for entity task:
#       error unless precisely the correct number of entities ranked

if ($task eq "background") {
    foreach $t (@topics) {
        if ($numret{$t} == 0) {
            &error("No documents retrieved for topic $t");
        }
        elsif ($numret{$t} > $MAX_RET) {
            &error("Too many documents ($numret{$t}) retrieved for topic $t");
        }    
    }
}
else {
    foreach $t (@topics) {
	if ($numret{$t} != $numents{$t}) {
	    &error("Expecting $numents{$t} entities ranked for topic $t, but found $numret{$t}");
	}
    }
}


print ERRLOG "Finished processing $results_file\n";
close ERRLOG || die "Close failed for error log $errlog: $!\n";
if ($num_errors) {
    exit 255;
}
exit 0;


# print error message, keeping track of total number of errors
sub error {
    my $msg_string = pop(@_);

    print ERRLOG 
	"$0 of $results_file: Error on line $line_num --- $msg_string\n";

    $num_errors++;
    if ($num_errors > $MAX_ERRORS) {
        print ERRLOG "$0 of $results_file: Quit. Too many errors!\n";
        close ERRLOG ||
	    die "Close failed for error log $errlog: $!\n";
	exit 255;
    }
}

