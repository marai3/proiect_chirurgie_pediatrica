// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MedicalLog {
    struct AccessEvent {
<<<<<<< HEAD
        address user;          
        string userRole;      
        string patientId;       
        string eventType;       
        uint256 timestamp;      
=======
        address user;
        string patientId;
        string eventType;
        uint256 timestamp;
>>>>>>> 4de70005ada7e99a8eb21320c7e745b4696340fe
    }

    AccessEvent[] public logs;

    event NewLog(
        address indexed user,
<<<<<<< HEAD
        string userRole,
=======
>>>>>>> 4de70005ada7e99a8eb21320c7e745b4696340fe
        string patientId,
        string eventType,
        uint256 timestamp
    );

<<<<<<< HEAD
    function logEvent(
        string memory _userRole,
        string memory _patientId,
        string memory _eventType
    ) public {
        logs.push(AccessEvent(msg.sender, _userRole, _patientId, _eventType, block.timestamp));
        emit NewLog(msg.sender, _userRole, _patientId, _eventType, block.timestamp);
=======
    function logEvent(string memory _patientId, string memory _eventType) public {
        logs.push(AccessEvent(msg.sender, _patientId, _eventType, block.timestamp));
        emit NewLog(msg.sender, _patientId, _eventType, block.timestamp);
>>>>>>> 4de70005ada7e99a8eb21320c7e745b4696340fe
    }

    function getLogCount() public view returns (uint256) {
        return logs.length;
    }
<<<<<<< HEAD

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
=======
}
>>>>>>> 4de70005ada7e99a8eb21320c7e745b4696340fe
