-- Migration: Add RBAC and Shared Data Sources
-- Date: 2025-11-03
-- Description: Add role to users, update database_connections for shared access

-- ==================================================================
-- Step 1: Add role column to users table
-- ==================================================================

ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'analyst' NOT NULL;

-- Update existing admin user to have admin role
UPDATE users SET role = 'admin' WHERE is_superuser = true OR username = 'admin';

-- ==================================================================
-- Step 2: Update database_connections table
-- ==================================================================

-- Rename user_id to created_by
DO $$
BEGIN
    IF EXISTS(
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='database_connections' AND column_name='user_id'
    ) THEN
        ALTER TABLE database_connections RENAME COLUMN user_id TO created_by;
    END IF;
END $$;

-- Add new columns for sharing and access control
ALTER TABLE database_connections 
ADD COLUMN IF NOT EXISTS is_shared BOOLEAN DEFAULT false NOT NULL,
ADD COLUMN IF NOT EXISTS access_level VARCHAR(50) DEFAULT 'public' NOT NULL,
ADD COLUMN IF NOT EXISTS allowed_roles JSONB,
ADD COLUMN IF NOT EXISTS allowed_users JSONB,
ADD COLUMN IF NOT EXISTS display_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS keywords JSONB;

-- ==================================================================
-- Step 3: Create indexes for performance
-- ==================================================================

CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_database_connections_is_shared ON database_connections(is_shared);
CREATE INDEX IF NOT EXISTS idx_database_connections_access_level ON database_connections(access_level);

-- ==================================================================
-- Step 4: Update existing database_connections to be shared
-- ==================================================================

-- Make existing connections shared and public by default
UPDATE database_connections 
SET is_shared = true, 
    access_level = 'public'
WHERE is_shared = false;

COMMIT;
