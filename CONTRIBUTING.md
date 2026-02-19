# Contributing

Thanks for your interest in contributing to hyprhalt!

## How to Contribute

1. Fork the repository and create a new branch
2. Make your changes
3. Test manually on a running Hyprland session
4. Submit a pull request

## Testing

This project requires a live Hyprland session to test properly. There are no automated tests - please verify your changes work as expected before submitting.

## Documentation

The project uses man pages as the primary documentation source. When modifying documentation:

1. **Only edit** `docs/hyprhalt.1` (the man page source file)
2. After modifying the man page, regenerate the markdown version:
   ```bash
   cd docs
   pandoc -s -f man -t markdown hyprhalt.1 -o hyprhalt.1.md
   ```
3. **Do not edit** `docs/hyprhalt.1.md` directly - it will be overwritten when regenerated from the man page

The markdown file is provided for easy viewing on GitHub, but the man page is the authoritative source.

## License

By contributing to this project, you agree to release your contributions into the public domain under the Unlicense. This means you waive all copyright and related rights to your contributed code.

If your contribution includes code from other sources or you cannot release your work into the public domain, please clearly state this in your pull request so appropriate licensing can be applied to that specific contribution.

## Questions?

Feel free to open an issue for discussion before starting work on major changes.
