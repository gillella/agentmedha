/**
 * PWA Icon Generator Script
 * 
 * This script generates all required PWA icons from the base SVG favicon.
 * 
 * Usage: node scripts/generate-pwa-icons.js
 * 
 * Requirements: 
 *   npm install sharp
 * 
 * Alternatively, you can use online tools like:
 *   - https://realfavicongenerator.net/
 *   - https://www.pwabuilder.com/imageGenerator
 */

const fs = require('fs');
const path = require('path');

// Icon sizes needed for PWA
const ICON_SIZES = [
    { name: 'favicon-16x16.png', size: 16 },
    { name: 'favicon-32x32.png', size: 32 },
    { name: 'pwa-64x64.png', size: 64 },
    { name: 'pwa-192x192.png', size: 192 },
    { name: 'pwa-512x512.png', size: 512 },
    { name: 'apple-touch-icon.png', size: 180 },
    { name: 'maskable-icon-512x512.png', size: 512 },
    { name: 'shortcut-social.png', size: 96 },
    { name: 'shortcut-email.png', size: 96 },
];

async function generateIcons() {
    try {
        // Try to use sharp for PNG generation
        const sharp = require('sharp');
        const svgPath = path.join(__dirname, '../public/favicon.svg');
        const svgContent = fs.readFileSync(svgPath);

        console.log('Generating PWA icons...\n');

        for (const icon of ICON_SIZES) {
            const outputPath = path.join(__dirname, '../public', icon.name);
            
            await sharp(svgContent)
                .resize(icon.size, icon.size)
                .png()
                .toFile(outputPath);
            
            console.log(`✓ Generated ${icon.name} (${icon.size}x${icon.size})`);
        }

        // Generate favicon.ico (multi-size)
        console.log('\n✓ All icons generated successfully!');
        console.log('\nNote: For favicon.ico, use an online converter or imagemagick.');
        
    } catch (error) {
        if (error.code === 'MODULE_NOT_FOUND') {
            console.log('Sharp not installed. Installing...');
            console.log('Run: npm install sharp');
            console.log('\nAlternatively, use these online tools to generate icons:');
            console.log('  - https://realfavicongenerator.net/');
            console.log('  - https://www.pwabuilder.com/imageGenerator');
            console.log('\nUpload your favicon.svg and download the generated icons.');
        } else {
            console.error('Error generating icons:', error);
        }
    }
}

// Instructions if run without sharp
console.log('='.repeat(50));
console.log('PWA Icon Generator for agentMedha');
console.log('='.repeat(50));
console.log('\nRequired icons:');
ICON_SIZES.forEach(icon => {
    console.log(`  - ${icon.name} (${icon.size}x${icon.size})`);
});
console.log('\nTo generate icons automatically, install sharp:');
console.log('  npm install sharp');
console.log('  node scripts/generate-pwa-icons.js');
console.log('\nOr use online tools:');
console.log('  - https://realfavicongenerator.net/');
console.log('  - https://www.pwabuilder.com/imageGenerator');
console.log('='.repeat(50));

// Try to generate if sharp is available
generateIcons();

