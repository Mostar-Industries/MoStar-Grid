/**
 * MoScript: Cost Optimization Oracle
 * Detects cost-saving opportunities by comparing routes and methods
 */

import { MoScript } from '../../types/moscript';

interface ShipmentData {
  route: string;
  method: 'air' | 'sea' | 'road' | 'rail';
  cost: number;
  weight: number; // kg
  date: Date;
}

interface CostSavingOpportunity {
  route: string;
  currentMethod: string;
  currentAvgCost: number;
  suggestedMethod: string;
  suggestedAvgCost: number;
  potentialSavings: number;
  savingsPercentage: number;
}

function detectSavingsRoutes(
  shipmentData: ShipmentData[],
  historical?: ShipmentData[]
): CostSavingOpportunity[] {
  const allData = historical ? [...shipmentData, ...historical] : shipmentData;
  
  // Group by route and method
  const routeMethodMap = new Map<string, Map<string, { costs: number[]; weights: number[] }>>();
  
  allData.forEach(shipment => {
    if (!routeMethodMap.has(shipment.route)) {
      routeMethodMap.set(shipment.route, new Map());
    }
    
    const methodMap = routeMethodMap.get(shipment.route)!;
    if (!methodMap.has(shipment.method)) {
      methodMap.set(shipment.method, { costs: [], weights: [] });
    }
    
    const methodData = methodMap.get(shipment.method)!;
    methodData.costs.push(shipment.cost);
    methodData.weights.push(shipment.weight);
  });

  const opportunities: CostSavingOpportunity[] = [];
  
  // Find routes with multiple shipping methods and compare costs
  routeMethodMap.forEach((methodMap, route) => {
    if (methodMap.size < 2) return; // Need at least 2 methods to compare
    
    const methodAverages = new Map<string, number>();
    
    methodMap.forEach((data, method) => {
      const avgCost = data.costs.reduce((sum, c) => sum + c, 0) / data.costs.length;
      methodAverages.set(method, avgCost);
    });
    
    // Find current most used method (assume it's the one with most data points)
    let currentMethod = '';
    let maxDataPoints = 0;
    methodMap.forEach((data, method) => {
      if (data.costs.length > maxDataPoints) {
        maxDataPoints = data.costs.length;
        currentMethod = method;
      }
    });
    
    const currentAvgCost = methodAverages.get(currentMethod)!;
    
    // Find cheaper alternatives
    methodAverages.forEach((avgCost, method) => {
      if (method !== currentMethod && avgCost < currentAvgCost) {
        const potentialSavings = currentAvgCost - avgCost;
        const savingsPercentage = (potentialSavings / currentAvgCost) * 100;
        
        if (savingsPercentage > 10) { // Only flag if savings > 10%
          opportunities.push({
            route,
            currentMethod,
            currentAvgCost,
            suggestedMethod: method,
            suggestedAvgCost: avgCost,
            potentialSavings,
            savingsPercentage
          });
        }
      }
    });
  });
  
  // Sort by savings percentage (highest first)
  opportunities.sort((a, b) => b.savingsPercentage - a.savingsPercentage);
  
  return opportunities;
}

export const mo_COST_ALERT: MoScript = {
  id: 'mo-cost-saver-007',
  name: 'Cost Optimization Oracle',
  trigger: 'onMonthlyTrendUpdate',
  inputs: ['shipmentData', 'historical'],
  logic: ({ shipmentData, historical }: { shipmentData: ShipmentData[]; historical?: ShipmentData[] }) => {
    return detectSavingsRoutes(shipmentData, historical);
  },
  voiceLine: (result: CostSavingOpportunity[]) => {
    if (result.length === 0) {
      return `All routes optimized. Either you're brilliant, or the bar is *very* low. I'll let you decide.`;
    }
    
    const top = result[0];
    return `Ka-ching! A ${top.savingsPercentage.toFixed(0)}% drop spotted on ${top.route} if you swap to ${top.suggestedMethod}. ` +
           `That's $${top.potentialSavings.toFixed(2)} saved per shipment — enough for office snacks *and* ego boosts.`;
  },
  sass: true
};
