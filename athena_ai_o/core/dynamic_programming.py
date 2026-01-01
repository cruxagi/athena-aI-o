"""
Dynamic Programming: Optimal policy computation for cognitive decision-making.

Implements value iteration and policy iteration algorithms for finding
optimal policies in Markov Decision Processes (MDPs).
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class PolicyType(Enum):
    """Types of policies that can be computed."""
    DETERMINISTIC = "deterministic"
    STOCHASTIC = "stochastic"


@dataclass
class State:
    """Represents a state in the MDP."""
    id: str
    value: float = 0.0
    
    
@dataclass
class Action:
    """Represents an action in the MDP."""
    id: str
    
    
@dataclass
class Transition:
    """Represents a state transition."""
    from_state: str
    action: str
    to_state: str
    probability: float
    reward: float


class DynamicProgramming:
    """
    Dynamic Programming for optimal policy computation.
    
    Implements value iteration and policy iteration for finding
    optimal policies in cognitive decision-making processes.
    """
    
    def __init__(self, gamma: float = 0.9, theta: float = 1e-6):
        """
        Initialize Dynamic Programming solver.
        
        Args:
            gamma: Discount factor (0 < γ < 1)
            theta: Convergence threshold for value iteration
        """
        self.gamma = gamma  # Discount factor
        self.theta = theta  # Convergence threshold
        
        self.states: Dict[str, State] = {}
        self.actions: Dict[str, Action] = {}
        self.transitions: List[Transition] = []
        
        # Policy: maps state_id -> action_id
        self.policy: Dict[str, str] = {}
        
        # Value function: maps state_id -> value
        self.value_function: Dict[str, float] = {}
        
        # Q-values: maps (state_id, action_id) -> Q-value
        self.q_values: Dict[Tuple[str, str], float] = {}
        
    def add_state(self, state_id: str, initial_value: float = 0.0) -> None:
        """Add a state to the MDP."""
        self.states[state_id] = State(id=state_id, value=initial_value)
        self.value_function[state_id] = initial_value
        
    def add_action(self, action_id: str) -> None:
        """Add an action to the MDP."""
        self.actions[action_id] = Action(id=action_id)
        
    def add_transition(self, from_state: str, action: str, to_state: str,
                      probability: float, reward: float) -> None:
        """
        Add a transition to the MDP.
        
        Args:
            from_state: Starting state ID
            action: Action ID
            to_state: Resulting state ID
            probability: Transition probability
            reward: Immediate reward
        """
        transition = Transition(
            from_state=from_state,
            action=action,
            to_state=to_state,
            probability=probability,
            reward=reward
        )
        self.transitions.append(transition)
        
    def get_transitions_for_state_action(self, state_id: str, action_id: str) -> List[Transition]:
        """Get all transitions for a given state-action pair."""
        return [
            t for t in self.transitions
            if t.from_state == state_id and t.action == action_id
        ]
        
    def get_available_actions(self, state_id: str) -> List[str]:
        """Get all available actions from a given state."""
        actions = set()
        for t in self.transitions:
            if t.from_state == state_id:
                actions.add(t.action)
        return list(actions)
        
    def calculate_q_value(self, state_id: str, action_id: str) -> float:
        """
        Calculate Q-value for a state-action pair.
        
        Q(s,a) = Σ P(s'|s,a) [R(s,a,s') + γ·V(s')]
        
        Args:
            state_id: State identifier
            action_id: Action identifier
            
        Returns:
            Q-value
        """
        transitions = self.get_transitions_for_state_action(state_id, action_id)
        
        q_value = 0.0
        for t in transitions:
            next_state_value = self.value_function.get(t.to_state, 0.0)
            q_value += t.probability * (t.reward + self.gamma * next_state_value)
            
        return q_value
        
    def value_iteration(self, max_iterations: int = 1000) -> Dict:
        """
        Perform value iteration to find optimal value function.
        
        Algorithm:
        1. Initialize V(s) for all states
        2. Repeat until convergence:
           V(s) ← max_a Σ P(s'|s,a)[R(s,a,s') + γ·V(s')]
        
        Args:
            max_iterations: Maximum number of iterations
            
        Returns:
            Dictionary with iteration results
        """
        iteration = 0
        converged = False
        
        for iteration in range(max_iterations):
            delta = 0.0
            
            # Update value for each state
            for state_id in self.states:
                old_value = self.value_function[state_id]
                
                # Get available actions
                actions = self.get_available_actions(state_id)
                if not actions:
                    continue
                    
                # Find max Q-value over all actions
                max_q = float('-inf')
                for action_id in actions:
                    q = self.calculate_q_value(state_id, action_id)
                    max_q = max(max_q, q)
                    
                # Update value function
                self.value_function[state_id] = max_q
                
                # Track maximum change
                delta = max(delta, abs(old_value - max_q))
                
            # Check for convergence
            if delta < self.theta:
                converged = True
                break
                
        return {
            'converged': converged,
            'iterations': iteration + 1,
            'final_delta': delta,
            'value_function': self.value_function.copy()
        }
        
    def extract_policy(self) -> Dict[str, str]:
        """
        Extract optimal policy from value function.
        
        π(s) = argmax_a Q(s,a)
        
        Returns:
            Policy mapping state_id -> action_id
        """
        policy = {}
        
        for state_id in self.states:
            actions = self.get_available_actions(state_id)
            if not actions:
                continue
                
            # Find action with maximum Q-value
            best_action = None
            best_q = float('-inf')
            
            for action_id in actions:
                q = self.calculate_q_value(state_id, action_id)
                self.q_values[(state_id, action_id)] = q
                
                if q > best_q:
                    best_q = q
                    best_action = action_id
                    
            if best_action:
                policy[state_id] = best_action
                
        self.policy = policy
        return policy
        
    def policy_iteration(self, max_iterations: int = 100) -> Dict:
        """
        Perform policy iteration to find optimal policy.
        
        Algorithm:
        1. Initialize policy π
        2. Repeat:
           a. Policy Evaluation: compute V^π
           b. Policy Improvement: π' = greedy(V^π)
           c. If π' = π, stop
        
        Args:
            max_iterations: Maximum number of iterations
            
        Returns:
            Dictionary with iteration results
        """
        # Initialize random policy
        for state_id in self.states:
            actions = self.get_available_actions(state_id)
            if actions:
                self.policy[state_id] = actions[0]
                
        iteration = 0
        policy_stable = False
        
        for iteration in range(max_iterations):
            # Policy Evaluation
            self._policy_evaluation()
            
            # Policy Improvement
            old_policy = self.policy.copy()
            self.extract_policy()
            
            # Check if policy is stable
            if old_policy == self.policy:
                policy_stable = True
                break
                
        return {
            'converged': policy_stable,
            'iterations': iteration + 1,
            'policy': self.policy.copy(),
            'value_function': self.value_function.copy()
        }
        
    def _policy_evaluation(self, max_iterations: int = 100) -> None:
        """
        Evaluate current policy to compute V^π.
        
        V^π(s) = Σ P(s'|s,π(s))[R(s,π(s),s') + γ·V^π(s')]
        """
        for _ in range(max_iterations):
            delta = 0.0
            
            for state_id in self.states:
                if state_id not in self.policy:
                    continue
                    
                old_value = self.value_function[state_id]
                action_id = self.policy[state_id]
                
                # Calculate value under current policy
                new_value = self.calculate_q_value(state_id, action_id)
                self.value_function[state_id] = new_value
                
                delta = max(delta, abs(old_value - new_value))
                
            if delta < self.theta:
                break
                
    def get_optimal_action(self, state_id: str) -> Optional[str]:
        """
        Get optimal action for a given state.
        
        Args:
            state_id: State identifier
            
        Returns:
            Optimal action ID or None
        """
        return self.policy.get(state_id)
        
    def get_state_value(self, state_id: str) -> float:
        """Get value of a state."""
        return self.value_function.get(state_id, 0.0)
        
    def get_state_summary(self) -> Dict:
        """Get summary of the MDP state."""
        return {
            'num_states': len(self.states),
            'num_actions': len(self.actions),
            'num_transitions': len(self.transitions),
            'gamma': self.gamma,
            'theta': self.theta,
            'policy_defined': len(self.policy) > 0,
            'value_function_defined': len(self.value_function) > 0
        }
