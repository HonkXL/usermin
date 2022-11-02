#!/usr/local/bin/perl
# For each message in each folder that has been marked as special, add it to
# the Special folder
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';

require './mailbox-lib.pl';
my $special = &get_special_folder();
$special || &error("Special folder not found!?");
my %mems = map { &folder_name($_->[0])."/".$_->[1], 1 } @{$special->{'members'}};

# For each message in each folder which is marked as special, check if it is
# already in the special folder
my @add;
foreach my $folder (&list_folders()) {
	next if ($folder eq $special);
	my @mails;
	eval {
		no warnings "once";
		$main::error_must_die = 1;
		use warnings "once";
		@mails = &mailbox_list_mails(undef, undef, $folder, 0);
		};
	next if ($@);
	foreach my $mail (@mails) {
		my $read = &get_mail_read($folder, $mail);
		if ($read & 2) {
			my ($realfolder, $realid) = &get_underlying_folder(
							$folder, $mail);
			my $key = &folder_name($realfolder)."/".$realid;
			if (!$mems{$key}) {
				push(@add, [ $realfolder, $realid ]);
				}
			}
		}
	}

# Add any that are missing
if (@add) {
	push(@{$special->{'members'}}, @add);
	&save_folder($special, $special);
	}

&redirect("index.cgi?id=".&urlize($special->{'id'}));
