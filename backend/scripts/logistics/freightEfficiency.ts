/**
 * MoScript: Freight Forwarder Efficiency Ranker
 * Analyzes shipment data to rank forwarders by performance metrics
 */

import { MoScript } from '../../types/moscript';

interface ShipmentData {
  forwarder: string;
  deliveryTime: number; // days
  cost: number;
  onTime: boolean;
  route: string;
}

interface ForwarderRanking {
  name: string;
  avgDeliveryTime: number;
  avgCost: number;
  onTimePercentage: number;
  totalShipments: number;
  score: number;
}

function rankForwarders(shipmentData: ShipmentData[]): { top: ForwarderRanking; rankings: ForwarderRanking[] } {
  const forwarderMap = new Map<string, ShipmentData[]>();
  
  // Group by forwarder
  shipmentData.forEach(shipment => {
    if (!forwarderMap.has(shipment.forwarder)) {
      forwarderMap.set(shipment.forwarder, []);
    }
    forwarderMap.get(shipment.forwarder)!.push(shipment);
  });

  // Calculate metrics for each forwarder
  const rankings: ForwarderRanking[] = [];
  
  forwarderMap.forEach((shipments, forwarder) => {
    const totalShipments = shipments.length;
    const avgDeliveryTime = shipments.reduce((sum, s) => sum + s.deliveryTime, 0) / totalShipments;
    const avgCost = shipments.reduce((sum, s) => sum + s.cost, 0) / totalShipments;
    const onTimeCount = shipments.filter(s => s.onTime).length;
    const onTimePercentage = (onTimeCount / totalShipments) * 100;
    
    // Composite score: lower is better (weighted avg of normalized metrics)
    const score = (avgDeliveryTime * 0.4) + (avgCost * 0.3) + ((100 - onTimePercentage) * 0.3);
    
    rankings.push({
      name: forwarder,
      avgDeliveryTime,
      avgCost,
      onTimePercentage,
      totalShipments,
      score
    });
  });

  // Sort by score (lower is better)
  rankings.sort((a, b) => a.score - b.score);
  
  return {
    top: rankings[0],
    rankings
  };
}

export const mo_FWD_EFFICIENCY: MoScript = {
  id: 'mo-fwd-eff-001',
  name: 'Forwarder Efficiency Ranker',
  trigger: 'onCalculateResults',
  inputs: ['shipmentData'],
  logic: ({ shipmentData }: { shipmentData: ShipmentData[] }) => {
    return rankForwarders(shipmentData);
  },
  voiceLine: (result: { top: ForwarderRanking; rankings: ForwarderRanking[] }) =>
    `After scouring every shipment, the data speaks: ${result.top.name} leads the pack — part cheetah, part calculator. ` +
    `${result.top.onTimePercentage.toFixed(1)}% on-time delivery, ${result.top.avgDeliveryTime.toFixed(1)} days average. *Chef's kiss.*`,
  sass: true
};
