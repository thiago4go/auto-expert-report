/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html", // Scan Jinja templates
    "./studyguide/**/*.py", // Scan Python files for potential class names (less common)
    "./app/**/*.py", // Scan Streamlit app files
  ],
  theme: {
    extend: {
      // Add custom theme extensions here if needed
      // Example:
      // colors: {
      //   'brand-blue': '#1992d4',
      // },
      // fontFamily: {
      //   sans: ['Inter var', ...defaultTheme.fontFamily.sans],
      // },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    // Add other plugins like @tailwindcss/forms if needed
  ],
}
