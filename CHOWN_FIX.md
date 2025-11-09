# Chown User Error Fix

## Problem

When running `install.sh`, the script fails at Step 7 with:

```
chown: invalid user: 'pi:pi'
```

This happens because the 'pi' user doesn't exist on your Raspberry Pi system. This can occur if:
- The user was deleted or never created
- You're using a custom Raspberry Pi image without the default 'pi' user
- The system was set up with a different username

## Root Cause

The original script attempted to change directory ownership to the 'pi' user unconditionally:

```bash
chown pi:pi /home/pi/recordings
chown pi:pi /home/pi/Pictures
```

This fails on:
- Development machines (Windows, Mac, Linux without 'pi' user)
- Non-Raspberry Pi systems
- Docker containers
- Virtual machines without pre-configured users

## Solution

Added a check to verify the 'pi' user exists before attempting `chown`:

**Before:**
```bash
mkdir -p /home/pi/recordings
mkdir -p /home/pi/Pictures
chown pi:pi /home/pi/recordings
chown pi:pi /home/pi/Pictures
chmod 755 /home/pi/recordings
chmod 755 /home/pi/Pictures
```

**After:**
```bash
mkdir -p /home/pi/recordings
mkdir -p /home/pi/Pictures

# IMPORTANT: Only change ownership if 'pi' user exists
if id "pi" &>/dev/null; then
    chown pi:pi /home/pi/recordings
    chown pi:pi /home/pi/Pictures
fi

chmod 755 /home/pi/recordings
chmod 755 /home/pi/Pictures
```

## How It Works

1. **`id "pi"`** - Checks if the 'pi' user exists
2. **`&>/dev/null`** - Suppresses output (we only care about return code)
3. **`if ... then ... fi`** - Conditional block
4. **`chmod 755`** - Always runs (doesn't require specific user)

## Result

- On Raspberry Pi: Directories owned by 'pi' user (intended behavior)
- On other systems: Directories owned by current user (no error)
- In both cases: Proper permissions set

## When This Runs

This fix applies in these scenarios:

✓ Running on actual Raspberry Pi with 'pi' user
  → Ownership changed to 'pi:pi' (as intended)

✓ Running on development machine without 'pi' user
  → Ownership not changed (directories still usable)

✓ Running in container/VM without 'pi' user
  → Ownership not changed (no error)

## Testing

To test the fix:

**On Raspberry Pi (with 'pi' user):**
```bash
sudo bash install.sh
# Should work and set ownership to pi:pi
ls -l /home/pi/recordings
# Should show: pi pi (owner and group)
```

**On development machine (without 'pi' user):**
```bash
sudo bash install.sh
# Should work without chown error
ls -l /home/pi/recordings
# Should show: root root (or current user)
```

## Verification

The fix is working if:

1. Script completes Step 7 without `chown` error
2. Directories are created: `/home/pi/recordings`, `/home/pi/Pictures`
3. Directories have proper permissions: `755`
4. On Raspberry Pi: directories owned by 'pi:pi'
5. On other systems: no error, directories still usable

## Important Notes

- The `chmod 755` command always runs (it doesn't depend on user existence)
- This is a safety improvement - the script now works in more environments
- On Raspberry Pi, the intended ownership behavior is preserved
- This change does NOT affect functionality on Raspberry Pi systems

## Backwards Compatibility

✓ Fully backwards compatible
✓ No breaking changes
✓ Existing Raspberry Pi installations unaffected
✓ Script now works on non-Raspberry Pi systems

## Summary

The fix makes the installation script more robust by gracefully handling systems where the 'pi' user doesn't exist, while preserving the intended behavior on Raspberry Pi systems.
