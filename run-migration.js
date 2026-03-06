/**
 * Supabase SQL Migration Runner
 * Executes the user dashboard schema migration via REST API
 */

const fs = require('fs');
const path = require('path');

async function runMigration() {
  try {
    // Load environment variables
    const envPath = path.join(__dirname, '.env.local');
    const envContent = fs.readFileSync(envPath, 'utf8');
    
    const serviceRoleKey = envContent.match(/SUPABASE_SERVICE_ROLE_KEY=(.+)/)?.[1]?.trim();
    const supabaseUrl = envContent.match(/NEXT_PUBLIC_SUPABASE_URL=(.+)/)?.[1]?.trim();
    
    if (!serviceRoleKey || !supabaseUrl) {
      throw new Error('Missing Supabase credentials in .env.local');
    }

    // Load SQL migration file
    const sqlPath = path.join(__dirname, 'supabase', 'migrations', '001_user_dashboard.sql');
    const sqlContent = fs.readFileSync(sqlPath, 'utf8');
    
    console.log('🔄 Executing database migration...');
    console.log(`📂 SQL file: ${sqlPath}`);
    console.log(`🌐 Supabase URL: ${supabaseUrl}`);

    // Execute SQL via REST API
    const response = await fetch(`${supabaseUrl}/rest/v1/rpc/exec_sql`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${serviceRoleKey}`,
        'apikey': serviceRoleKey
      },
      body: JSON.stringify({
        sql: sqlContent
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Migration failed:', errorText);
      
      // Try alternative approach: direct SQL execution
      console.log('🔄 Trying alternative approach...');
      
      const altResponse = await fetch(`${supabaseUrl}/rest/v1/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/sql',
          'Authorization': `Bearer ${serviceRoleKey}`,
          'apikey': serviceRoleKey
        },
        body: sqlContent
      });

      if (!altResponse.ok) {
        const altErrorText = await altResponse.text();
        throw new Error(`Alternative approach failed: ${altErrorText}`);
      }

      console.log('✅ Migration completed via alternative approach!');
    } else {
      const result = await response.json();
      console.log('✅ Migration completed successfully!', result);
    }

    // Verify tables were created
    await verifyTables(supabaseUrl, serviceRoleKey);

  } catch (error) {
    console.error('❌ Migration failed:', error.message);
    console.log('\n📋 Manual steps required:');
    console.log('1. Go to Supabase Dashboard: https://app.supabase.com/');
    console.log('2. Navigate to SQL Editor');
    console.log('3. Copy and paste the contents of supabase/migrations/001_user_dashboard.sql');
    console.log('4. Execute the SQL manually');
    process.exit(1);
  }
}

async function verifyTables(supabaseUrl, serviceRoleKey) {
  try {
    console.log('🔍 Verifying created tables...');
    
    const tables = ['user_profiles', 'user_stocks', 'user_watchlist', 'user_notification_settings', 'user_notifications'];
    
    for (const table of tables) {
      const response = await fetch(`${supabaseUrl}/rest/v1/${table}?limit=1`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${serviceRoleKey}`,
          'apikey': serviceRoleKey
        }
      });
      
      if (response.ok) {
        console.log(`✅ Table '${table}' exists and is accessible`);
      } else {
        console.log(`⚠️  Table '${table}' may not exist or is not accessible`);
      }
    }
  } catch (error) {
    console.log('⚠️  Could not verify tables:', error.message);
  }
}

// Run the migration
runMigration();