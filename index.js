#!/usr/bin/env node

const { program } = require('commander');
const inquirer = require('inquirer');
const fs = require('fs-extra');
const path = require('path');
const chalk = require('chalk');

program
  .name('openclaw-skill-gen')
  .description('CLI for generating OpenClaw skill scaffolds')
  .version('1.0.0');

program
  .command('create')
  .description('Create a new OpenClaw skill')
  .action(async () => {
    const answers = await inquirer.prompt([
      {
        type: 'input',
        name: 'name',
        message: 'Skill name (e.g., qqbot-channel):',
        validate: (input) => input.length > 0 || 'Skill name is required',
      },
      {
        type: 'input',
        name: 'description',
        message: 'Skill description:',
        validate: (input) => input.length > 0 || 'Description is required',
      },
    ]);

    const skillDir = path.join(process.cwd(), answers.name);
    if (fs.existsSync(skillDir)) {
      console.error(chalk.red(`Directory ${answers.name} already exists.`));
      process.exit(1);
    }

    // Create skill directory
    fs.mkdirSync(skillDir);

    // Create SKILL.md
    const skillMd = `# ${answers.name}

${answers.description}

## Location
~/.openclaw/extensions/your-extension/skills/${answers.name}/SKILL.md

## Usage
Describe how to use this skill.

## Parameters
List any parameters the skill accepts.

## Examples
Provide usage examples.
`;
    fs.writeFileSync(path.join(skillDir, 'SKILL.md'), skillMd);

    // Create a basic implementation file (optional)
    const impl = `// Implementation for ${answers.name}
// This is a placeholder for the skill's actual implementation.
// You can replace this with your own logic.

exports.main = async (args) => {
  console.log('Skill ${answers.name} executed with args:', args);
  return { success: true, message: 'Skill executed' };
};
`;
    fs.writeFileSync(path.join(skillDir, 'index.js'), impl);

    // Create package.json for the skill (optional)
    const skillPackage = {
      name: `@openclaw/skill-${answers.name}`,
      version: '1.0.0',
      description: answers.description,
      main: 'index.js',
      author: 'OpenClaw User',
      license: 'MIT',
    };
    fs.writeJSONSync(path.join(skillDir, 'package.json'), skillPackage, { spaces: 2 });

    console.log(chalk.green(`Skill ${answers.name} created successfully at ${skillDir}`));
    console.log(chalk.green('Next steps:'));
    console.log(`  1. cd ${answers.name}`);
    console.log(`  2. Implement your skill logic in index.js`);
    console.log(`  3. Test your skill`);
    console.log(`  4. Publish to OpenClaw skill registry (if applicable)`);
  });

program.parse();