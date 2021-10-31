#!/usr/bin/perl
$|=1;
print "\@HELLO\n";
print STDERR "\@HELLO\n";

while(<>) {
  print "\@$_";
  print STDERR "\@$_";
}

print "\@GOODBYE\n";
print STDERR "\@GOODBYE\n";

