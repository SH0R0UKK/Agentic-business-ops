"""
SQLite database utilities for storing profiles and plans.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent / "business_ops.db"


def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def init_db():
    """Initialize database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create profiles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            startup_id TEXT PRIMARY KEY,
            business_name TEXT,
            business_type TEXT,
            sector TEXT,
            location TEXT,
            stage TEXT,
            data JSON NOT NULL,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    
    # Create plans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            plan_id TEXT PRIMARY KEY,
            startup_id TEXT NOT NULL,
            title TEXT,
            version INTEGER DEFAULT 1,
            data JSON NOT NULL,
            created_at TEXT,
            FOREIGN KEY (startup_id) REFERENCES profiles (startup_id)
        )
    """)
    
    # Create index for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_plans_startup 
        ON plans (startup_id, created_at DESC)
    """)
    
    conn.commit()
    conn.close()
    
    logger.info(f"✅ Database initialized at {DB_PATH}")


# ============================================================================
# PROFILE OPERATIONS
# ============================================================================

def save_profile(profile_data: Dict[str, Any]) -> bool:
    """
    Save or update a startup profile.
    
    Args:
        profile_data: Profile dictionary (from StartupProfile.model_dump())
    
    Returns:
        True if successful
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        startup_id = profile_data.get("startup_id")
        if not startup_id:
            raise ValueError("startup_id is required")
        
        now = datetime.utcnow().isoformat()
        
        # Check if profile exists
        cursor.execute("SELECT startup_id FROM profiles WHERE startup_id = ?", (startup_id,))
        exists = cursor.fetchone()
        
        if exists:
            # Update existing profile
            cursor.execute("""
                UPDATE profiles 
                SET business_name = ?,
                    business_type = ?,
                    sector = ?,
                    location = ?,
                    stage = ?,
                    data = ?,
                    updated_at = ?
                WHERE startup_id = ?
            """, (
                profile_data.get("business_name", ""),
                profile_data.get("business_type", ""),
                profile_data.get("sector", ""),
                profile_data.get("location", "Egypt"),
                profile_data.get("stage", ""),
                json.dumps(profile_data),
                now,
                startup_id
            ))
            logger.info(f"📝 Updated profile for {startup_id}")
        else:
            # Insert new profile
            cursor.execute("""
                INSERT INTO profiles (
                    startup_id, business_name, business_type, sector,
                    location, stage, data, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                startup_id,
                profile_data.get("business_name", ""),
                profile_data.get("business_type", ""),
                profile_data.get("sector", ""),
                profile_data.get("location", "Egypt"),
                profile_data.get("stage", ""),
                json.dumps(profile_data),
                now,
                now
            ))
            logger.info(f"➕ Created profile for {startup_id}")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error saving profile: {e}")
        return False


def get_profile(startup_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a startup profile by ID.
    
    Args:
        startup_id: Startup identifier
    
    Returns:
        Profile dictionary or None if not found
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT data FROM profiles WHERE startup_id = ?", (startup_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return json.loads(row["data"])
        return None
        
    except Exception as e:
        logger.error(f"❌ Error retrieving profile: {e}")
        return None


def list_profiles(limit: int = 100) -> List[Dict[str, Any]]:
    """
    List all profiles (limited).
    
    Args:
        limit: Maximum number of profiles to return
    
    Returns:
        List of profile dictionaries
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT startup_id, business_name, business_type, location, stage, created_at
            FROM profiles
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
        
    except Exception as e:
        logger.error(f"❌ Error listing profiles: {e}")
        return []


# ============================================================================
# PLAN OPERATIONS
# ============================================================================

def save_plan(plan_data: Dict[str, Any]) -> bool:
    """
    Save a plan.
    
    Args:
        plan_data: Plan dictionary (from Plan.model_dump())
    
    Returns:
        True if successful
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        plan_id = plan_data.get("plan_id")
        startup_id = plan_data.get("startup_id")
        
        if not plan_id or not startup_id:
            raise ValueError("plan_id and startup_id are required")
        
        cursor.execute("""
            INSERT INTO plans (plan_id, startup_id, title, version, data, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            plan_id,
            startup_id,
            plan_data.get("title", "Plan"),
            plan_data.get("version", 1),
            json.dumps(plan_data),
            plan_data.get("created_at", datetime.utcnow().isoformat())
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"💾 Saved plan {plan_id} for {startup_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error saving plan: {e}")
        return False


def get_plan(plan_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a plan by ID.
    
    Args:
        plan_id: Plan identifier
    
    Returns:
        Plan dictionary or None if not found
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT data FROM plans WHERE plan_id = ?", (plan_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return json.loads(row["data"])
        return None
        
    except Exception as e:
        logger.error(f"❌ Error retrieving plan: {e}")
        return None


def get_latest_plan(startup_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve the most recent plan for a startup.
    
    Args:
        startup_id: Startup identifier
    
    Returns:
        Plan dictionary or None if not found
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT data 
            FROM plans 
            WHERE startup_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (startup_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row["data"])
        return None
        
    except Exception as e:
        logger.error(f"❌ Error retrieving latest plan: {e}")
        return None


def list_plans_for_startup(startup_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    List all plans for a startup.
    
    Args:
        startup_id: Startup identifier
        limit: Maximum number of plans to return
    
    Returns:
        List of plan dictionaries
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT plan_id, title, version, created_at
            FROM plans
            WHERE startup_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (startup_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
        
    except Exception as e:
        logger.error(f"❌ Error listing plans: {e}")
        return []
