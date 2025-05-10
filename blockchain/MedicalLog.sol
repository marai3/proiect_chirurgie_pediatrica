// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MedicalLog {
    struct AccessEvent {
        address user;
        string patientId;
        string eventType;
        uint256 timestamp;
    }

    AccessEvent[] public logs;

    event NewLog(
        address indexed user,
        string patientId,
        string eventType,
        uint256 timestamp
    );

    function logEvent(string memory _patientId, string memory _eventType) public {
        logs.push(AccessEvent(msg.sender, _patientId, _eventType, block.timestamp));
        emit NewLog(msg.sender, _patientId, _eventType, block.timestamp);
    }

    function getLogCount() public view returns (uint256) {
        return logs.length;
    }
}