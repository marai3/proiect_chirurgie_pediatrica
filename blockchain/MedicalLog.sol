// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MedicalLog {
    struct AccessEvent {
        address user;          
        string userRole;      
        string patientId;       
        string eventType;       
        uint256 timestamp;      
    }

    AccessEvent[] public logs;

    event NewLog(
        address indexed user,
        string userRole,
        string patientId,
        string eventType,
        uint256 timestamp
    );

    function logEvent(
        string memory _userRole,
        string memory _patientId,
        string memory _eventType
    ) public {
        logs.push(AccessEvent(msg.sender, _userRole, _patientId, _eventType, block.timestamp));
        emit NewLog(msg.sender, _userRole, _patientId, _eventType, block.timestamp);
    }

    function getLogCount() public view returns (uint256) {
        return logs.length;
    }

    function getLogByIndex(uint256 index) public view returns (
        address user,
        string memory userRole,
        string memory patientId,
        string memory eventType,
        uint256 timestamp
    ) {
        require(index < logs.length, "Index invalid");
        AccessEvent memory e = logs[index];
        return (e.user, e.userRole, e.patientId, e.eventType, e.timestamp);
    }
}
