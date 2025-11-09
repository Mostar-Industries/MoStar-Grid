import React from 'react';
import { ReasoningStep, CulturalContext } from '../types';

interface EnhancedThinkingVisualizationProps {
  reasoningSteps: ReasoningStep[];
  culturalContext: CulturalContext;
}

const EnhancedThinkingVisualization: React.FC<EnhancedThinkingVisualizationProps> = ({ reasoningSteps, culturalContext }) => {
  return (
    <div className="thinking-process bg-yellow-50 border border-yellow-200 rounded-lg p-4 my-4 text-gray-800">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-lg font-semibold flex items-center">
          🧠 AI Cultural Reasoning Process
          <span className="ml-2 text-sm bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
            Ubuntu-Informed
          </span>
        </h4>
        <div className="flex space-x-2">
          <span className="text-sm text-gray-600">CARE Score: {culturalContext.careScore}%</span>
          <span className="text-sm text-gray-600">Cultural Accuracy: {culturalContext.culturalAccuracy}%</span>
        </div>
      </div>
      
      {reasoningSteps.map((step, index) => (
        <div key={index} className="reasoning-step bg-white border-l-4 border-blue-500 rounded-r p-3 mb-2 shadow-sm">
          <div className="step-header flex justify-between items-center mb-2">
            <div className="flex items-center space-x-2">
              <span className="step-number bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm">
                {index + 1}
              </span>
              <span className="step-type bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                {step.type}
              </span>
              {step.careValidated && (
                <span className="care-badge bg-green-100 text-green-800 text-xs px-2 py-1 rounded flex items-center">
                  <i className="fas fa-check-circle mr-1"></i> CARE Verified
                </span>
              )}
            </div>
            <span className="confidence-score text-sm font-medium">
              {step.confidence}% confidence
            </span>
          </div>
          
          <div className="step-content space-y-2">
            <p className="text-sm"><strong>Action:</strong> {step.action}</p>
            <div className="cultural-context bg-gray-50 p-2 rounded">
              <strong>Cultural Context:</strong> 
              <span className="text-sm ml-1">{step.culturalContext}</span>
              {step.culturalSources && (
                <div className="sources mt-1 text-xs text-gray-600">
                  <strong>Sources:</strong> {step.culturalSources.join(', ')}
                </div>
              )}
            </div>
            
            {step.symbolicLogic && (
              <div className="symbolic-logic bg-purple-50 p-2 rounded">
                <strong>Symbolic Logic:</strong> 
                <code className="block text-xs font-mono bg-white p-1 rounded mt-1 overflow-x-auto">
                  {step.symbolicLogic}
                </code>
              </div>
            )}
            
            {step.careBreakdown && (
              <div className="care-breakdown grid grid-cols-2 lg:grid-cols-4 gap-2 text-xs mt-2">
                <div className="p-2 bg-gray-50 rounded">
                  <div className="font-semibold">Collective Benefit</div>
                  <div className={`${step.careBreakdown.collectiveBenefit.score > 0.8 ? 'text-green-600' : 'text-yellow-600'} text-sm font-medium`}>
                    {Math.round(step.careBreakdown.collectiveBenefit.score * 100)}%
                  </div>
                  <p className="text-xs text-gray-600 mt-1 italic">{step.careBreakdown.collectiveBenefit.explanation}</p>
                </div>
                <div className="p-2 bg-gray-50 rounded">
                  <div className="font-semibold">Authority Control</div>
                  <div className={`${step.careBreakdown.authorityControl.score > 0.8 ? 'text-green-600' : 'text-yellow-600'} text-sm font-medium`}>
                    {Math.round(step.careBreakdown.authorityControl.score * 100)}%
                  </div>
                  <p className="text-xs text-gray-600 mt-1 italic">{step.careBreakdown.authorityControl.explanation}</p>
                </div>
                <div className="p-2 bg-gray-50 rounded">
                  <div className="font-semibold">Responsibility</div>
                  <div className={`${step.careBreakdown.responsibility.score > 0.8 ? 'text-green-600' : 'text-yellow-600'} text-sm font-medium`}>
                    {Math.round(step.careBreakdown.responsibility.score * 100)}%
                  </div>
                  <p className="text-xs text-gray-600 mt-1 italic">{step.careBreakdown.responsibility.explanation}</p>
                </div>
                <div className="p-2 bg-gray-50 rounded">
                  <div className="font-semibold">Ethics</div>
                  <div className={`${step.careBreakdown.ethics.score > 0.8 ? 'text-green-600' : 'text-yellow-600'} text-sm font-medium`}>
                    {Math.round(step.careBreakdown.ethics.score * 100)}%
                  </div>
                  <p className="text-xs text-gray-600 mt-1 italic">{step.careBreakdown.ethics.explanation}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default EnhancedThinkingVisualization;