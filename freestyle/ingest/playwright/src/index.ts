import 'dotenv/config';
import { withBrowser } from './core/browser';
import { createJob } from './jobs/createJob';
import { seedCategoryTasks } from './jobs/seedCategoryTasks';
import { getJob } from './jobs/getJob';
import { runWorker } from './jobs/runWorker';

type Args = { [k: string]: string | boolean };

function parseArgs(argv: string[]): { cmd: string; args: Args } {
  const [cmd, ...rest] = argv.slice(2);
  const args: Args = {};
  for (let i = 0; i < rest.length; i++) {
    const a = rest[i];
    if (a.startsWith('--')) {
      const key = a.replace(/^--/, '');
      const val = rest[i + 1] && !rest[i + 1].startsWith('--') ? rest[++i] : true;
      args[key] = val as string;
    }
  }
  return { cmd: cmd || 'help', args };
}

async function main() {
  const { cmd, args } = parseArgs(process.argv);
  if (cmd === 'help' || cmd === undefined) {
    console.log('Commands:');
    console.log('  init-job --category <url> --brand "Reformation"');
    console.log('  seed-tasks --job <id>');
    console.log('  run-worker --job <id> [--concurrency N]');
    process.exit(0);
  }

  if (cmd === 'init-job') {
    const brand = (args.brand as string) || 'Reformation';
    const category = args.category as string;
    if (!category) throw new Error('--category is required');
    const jobId = await createJob(brand, category);
    console.log(String(jobId));
    return;
  }

  if (cmd === 'seed-tasks') {
    const jobId = Number(args.job);
    if (!jobId) throw new Error('--job is required');
    const job = await getJob(jobId);
    if (!job) throw new Error(`job ${jobId} not found`);
    await withBrowser(browser => seedCategoryTasks(browser, jobId, job.category_url));
    return;
  }

  if (cmd === 'run-worker') {
    const jobId = Number(args.job);
    if (!jobId) throw new Error('--job is required');
    if (args.concurrency) process.env.MAX_CONCURRENCY = String(args.concurrency);
    await withBrowser(browser => runWorker(browser, jobId));
    return;
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});


