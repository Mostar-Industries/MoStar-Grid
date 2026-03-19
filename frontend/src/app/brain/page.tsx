import BrainVisualization from '@/components/BrainVisualization';
import GridNav from '@/components/GridNav';

export default function BrainPage() {
  return (
    <div style={{
      width: '100vw',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      background: 'linear-gradient(180deg, #001133 0%, #000011 50%, #000000 100%)'
    }}>
      <GridNav />
      <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
        <BrainVisualization />
      </div>
    </div>
  );
}
