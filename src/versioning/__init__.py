"""
Data versioning and snapshot management module.
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import shutil

@dataclass
class Snapshot:
    """Represents a data snapshot."""
    id: str  # Format: snapshot_YYYYMMDD_HHMMSS
    timestamp: str  # ISO format
    description: str
    user_role: str
    planning_state: Dict[str, Any]
    expenses: Dict[str, List[Dict]]
    expenses_closed: Dict[str, bool]
    
    def to_dict(self):
        """Convert snapshot to dictionary."""
        return asdict(self)

class VersionManager:
    """Manages data versioning and snapshots."""
    
    def __init__(self, snapshots_dir: Path = None):
        """Initialize version manager."""
        if snapshots_dir is None:
            snapshots_dir = Path(__file__).parent.parent / "data" / "snapshots"
        self.snapshots_dir = snapshots_dir
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.max_snapshots = 50
    
    def create_snapshot(
        self,
        description: str,
        user_role: str,
        planning_state: Dict[str, Any],
        expenses: Dict[str, List],
        expenses_closed: Dict[str, bool]
    ) -> Snapshot:
        """Create a new snapshot of the current state."""
        # Generate snapshot ID and timestamp
        now = datetime.now()
        snapshot_id = now.strftime("snapshot_%Y%m%d_%H%M%S")
        timestamp = now.isoformat()
        
        # Convert expenses to serializable format
        expenses_dict = {}
        for role, expense_list in expenses.items():
            expenses_dict[role] = [
                {k: v for k, v in expense.__dict__.items()}
                for expense in expense_list
            ]
        
        # Create snapshot object
        snapshot = Snapshot(
            id=snapshot_id,
            timestamp=timestamp,
            description=description,
            user_role=user_role,
            planning_state=planning_state,
            expenses=expenses_dict,
            expenses_closed=expenses_closed
        )
        
        # Save to file
        snapshot_path = self.snapshots_dir / f"{snapshot_id}.json"
        with open(snapshot_path, 'w', encoding='utf-8') as f:
            json.dump(snapshot.to_dict(), f, ensure_ascii=False, indent=2)
        
        # Clean up old snapshots if needed
        self._cleanup_old_snapshots()
        
        return snapshot
    
    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List all available snapshots."""
        snapshots = []
        
        for snapshot_file in sorted(self.snapshots_dir.glob("snapshot_*.json"), reverse=True):
            try:
                with open(snapshot_file, 'r', encoding='utf-8') as f:
                    snapshot_data = json.load(f)
                    # Only include metadata for listing
                    snapshots.append({
                        'id': snapshot_data['id'],
                        'timestamp': snapshot_data['timestamp'],
                        'description': snapshot_data['description'],
                        'user_role': snapshot_data['user_role'],
                        'planning_status': snapshot_data['planning_state'].get('status', 'UNKNOWN')
                    })
            except Exception as e:
                print(f"Error loading snapshot {snapshot_file}: {e}")
                continue
        
        return snapshots
    
    def load_snapshot(self, snapshot_id: str) -> Optional[Snapshot]:
        """Load a specific snapshot."""
        snapshot_path = self.snapshots_dir / f"{snapshot_id}.json"
        
        if not snapshot_path.exists():
            return None
        
        try:
            with open(snapshot_path, 'r', encoding='utf-8') as f:
                snapshot_data = json.load(f)
                return Snapshot(**snapshot_data)
        except Exception as e:
            print(f"Error loading snapshot {snapshot_id}: {e}")
            return None
    
    def get_snapshot_file_path(self, snapshot_id: str) -> Optional[Path]:
        """Get the file path for a snapshot."""
        snapshot_path = self.snapshots_dir / f"{snapshot_id}.json"
        return snapshot_path if snapshot_path.exists() else None
    
    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a specific snapshot."""
        snapshot_path = self.snapshots_dir / f"{snapshot_id}.json"
        
        if snapshot_path.exists():
            try:
                snapshot_path.unlink()
                return True
            except Exception as e:
                print(f"Error deleting snapshot {snapshot_id}: {e}")
                return False
        return False
    
    def _cleanup_old_snapshots(self):
        """Remove old snapshots if count exceeds max_snapshots."""
        snapshot_files = sorted(
            self.snapshots_dir.glob("snapshot_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        # Keep only the most recent max_snapshots
        for old_snapshot in snapshot_files[self.max_snapshots:]:
            try:
                old_snapshot.unlink()
                print(f"Deleted old snapshot: {old_snapshot.name}")
            except Exception as e:
                print(f"Error deleting old snapshot {old_snapshot}: {e}")
    
    def get_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        """Get the most recent snapshot metadata."""
        snapshots = self.list_snapshots()
        return snapshots[0] if snapshots else None

# Global version manager instance
version_manager = VersionManager()
