#ifndef INDEXLR_MINIMIZE_H
#define INDEXLR_MINIMIZE_H

// ntHash 2.0.0
#include "ntHashIterator.h"
#include "nthash.h"

#include <algorithm>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>

// Return true if the second string is a prefix of the string s.
template<size_t N>
static inline bool
startsWith(const std::string& s, const char (&prefix)[N])
{
	auto n = N - 1;
	return s.size() > n && equal(s.begin(), s.begin() + n, prefix);
}

struct HashAndPos
{
	HashAndPos(uint64_t hash, size_t pos)
	  : hash(hash)
	  , pos(pos)
	{}
	uint64_t hash;
	size_t pos;
};

using HashValues = std::vector<HashAndPos>;

// Hash the k-mers of a read using ntHash.
static inline HashValues
hashKmers(const std::string& readstr, const size_t k)
{
	HashValues hashes;
	if (readstr.size() < k) {
		return hashes;
	}
	hashes.reserve(readstr.size() - k + 1);
	for (ntHashIterator iter(readstr, 1, k); iter != ntHashIterator::end(); ++iter) {
		hashes.push_back(HashAndPos((*iter)[0], iter.pos()));
	}
	return hashes;
}

// Minimerize a sequence: Find the minimizers of a vector of hash values representing a sequence.
/* Algorithm
v is a vector of non-negative integers
w is the window size
Invariants
    0 <  w <= v.size() - 1
    0 <= l <= r <= v.size() - 1
Initial conditions
    M    = NIL       Final set of minimizers, empty initially
    min  = -1        Minimum element
    i    = -1        Index of minimum element
    prev = -1        Index of previous minimum element
    l    = 0         Index of left end of window
    r    = l + w - 1 Index of right end of window
Computation
At each window, if the previous minimum is out of scope, find the new, right-most, minimum
or else, check with only the right-most element to determine if that is the new minimum.
A minimizer is added to the final vector only if it's index has changed.
for each window of v bounded by [l, r]
    if (i < l)
        i = index of minimum element in [l, r], furthest from l.
    else if (v[r] <= v[i])
        i = r
    min = v[i]
    if (i != prev) {
        prev = i
        M <- M + m
    }
    l = l + 1        Move window's left bound by one element
    r = l + w - 1    Set window's right bound
}*/

static inline HashValues
getMinimizers(const HashValues& hashes, const unsigned w)
{
	HashValues minimizers;
	if (hashes.size() < w) {
		return minimizers;
	}
	minimizers.reserve(2 * hashes.size() / w);
	int i = -1, prev = -1;
	auto firstIt = hashes.begin();
	auto minIt = hashes.end();
	for (auto leftIt = firstIt; leftIt < hashes.end() - w + 1; ++leftIt) {
		auto rightIt = leftIt + w;
		if (i < leftIt - firstIt) {
			// Use of operator '<=' returns the minimum that is furthest from left.
			minIt = std::min_element(leftIt, rightIt, [](const HashAndPos& a, const HashAndPos& b) {
				return a.hash <= b.hash;
			});
		} else if (rightIt[-1].hash <= minIt->hash) {
			minIt = rightIt - 1;
		}
		i = minIt - firstIt;
		if (i > prev) {
			prev = i;
			minimizers.push_back(*minIt);
		}
	}
	return minimizers;
}

// Test the condition of a I/O stream.
static inline void
assert_good(const std::ios& stream, const std::string& path)
{
	if (!stream.good()) {
		std::cerr << "error: " << std::strerror(errno) << ": " << path << '\n';
		exit(EXIT_FAILURE);
	}
}

#endif