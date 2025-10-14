# -*- coding: utf-8 -*-
"""
ИКС Анализатор Системы - Основные модули
"""

__version__ = "1.0.0"
__author__ = "ИКС Анализатор Системы"

from .system_model import SystemModel, Node, Link, NodeType, LinkType
from .reliability import ReliabilityAnalyzer, FailureType, FailureEvent, FaultTree
from .simulation import NetworkSimulator, SimulationEvent, EventType
from .stress_test import StressTester, StressTestType, StressTestScenario, StressTestResult
from .whatif import WhatIfAnalyzer, ParameterType, ParameterRange, WhatIfScenario, WhatIfResult

__all__ = [
    'SystemModel', 'Node', 'Link', 'NodeType', 'LinkType',
    'ReliabilityAnalyzer', 'FailureType', 'FailureEvent', 'FaultTree',
    'NetworkSimulator', 'SimulationEvent', 'EventType',
    'StressTester', 'StressTestType', 'StressTestScenario', 'StressTestResult',
    'WhatIfAnalyzer', 'ParameterType', 'ParameterRange', 'WhatIfScenario', 'WhatIfResult'
]