import 'dotenv/config';

console.log('Node sees DATABASE_URL=', process.env.DATABASE_URL || '');
console.log('Node sees SUPABASE_URL=', process.env.SUPABASE_URL || '');
console.log('Node sees SUPABASE_STORAGE_BUCKET=', process.env.SUPABASE_STORAGE_BUCKET || '');
