// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title DocumentRegistry
/// @notice Anchors document hashes (e.g. the inventory PDF's SHA-256) on-chain
///         for tamper-evidence. Stores only the hash + the time it was first
///         anchored — never the document itself.
contract DocumentRegistry {
    /// @dev hash => unix timestamp of the first anchoring (0 = not anchored).
    mapping(bytes32 => uint256) public anchoredAt;

    event Anchored(bytes32 indexed hash, uint256 timestamp);

    /// @notice Anchor a document hash. First-write-wins: re-anchoring an
    ///         existing hash preserves the original timestamp.
    function anchor(bytes32 hash) external {
        if (anchoredAt[hash] == 0) {
            anchoredAt[hash] = block.timestamp;
            emit Anchored(hash, block.timestamp);
        }
    }

    /// @notice Return the anchoring timestamp for a hash (0 if not anchored).
    function verify(bytes32 hash) external view returns (uint256) {
        return anchoredAt[hash];
    }
}
