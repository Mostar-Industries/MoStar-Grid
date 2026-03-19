import BrainVisualization from '@/components/BrainVisualization';
import styles from '@/components/BrainVisualization.module.css';
import GridNav from '@/components/GridNav';

export default function BrainPage() {
  return (
    <div className={styles.brainContainer}>
      <GridNav />
      <BrainVisualization />
    </div>
  );
}
