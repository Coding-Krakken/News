# User Guide

## Getting Started

### Creating an Account

1. Visit the News application homepage
2. Click "Sign Up" in the navigation bar
3. Enter your email address
4. Create a strong password (minimum 8 characters with uppercase, lowercase, and numbers)
5. Optionally, add a display name
6. Click "Sign Up"

You'll be automatically logged in after successful registration.

### Logging In

1. Click "Login" in the navigation bar
2. Enter your email and password
3. Click "Login"

### Logging Out

Click the "Logout" button in the navigation bar. This will end your session and require you to log in again.

## Managing Your Profile

### Viewing Your Profile

1. Click "Profile" in the navigation bar
2. View your current profile information:
   - Email address (cannot be changed)
   - Display name
   - Avatar URL

### Editing Your Profile

1. Go to your Profile page
2. Click "Edit Profile"
3. Update your display name and/or avatar URL
4. Click "Save"

Your changes will be saved immediately.

## Working with Bookmarks

### What are Bookmarks?

Bookmarks allow you to save articles and stories for easy access later. When you bookmark an item, it's added to your personal collection.

### Viewing Your Bookmarks

1. Click "Bookmarks" in the navigation bar
2. See all your saved articles and stories
3. Items are listed with their type (article/story) and ID

### Removing Bookmarks

1. Go to your Bookmarks page
2. Find the bookmark you want to remove
3. Click the "Remove" button next to it

## Using Saved Filters

### What are Saved Filters?

Saved filters help you quickly access news that matches specific criteria. You can create multiple filters for different topics or interests.

### Creating a Saved Filter

1. Click "Filters" in the navigation bar
2. Click "Add New Filter"
3. Enter a name for your filter (e.g., "Tech News")
4. Enter your filter criteria in JSON format:
   ```json
   {
     "category": "technology",
     "language": "en",
     "source": "techcrunch"
   }
   ```
5. Click "Save Filter"

### Filter Query Examples

**Technology news in English:**
```json
{
  "category": "tech",
  "language": "en"
}
```

**Business news from specific sources:**
```json
{
  "category": "business",
  "sources": ["bloomberg", "wsj"]
}
```

**Sports news excluding certain topics:**
```json
{
  "category": "sports",
  "exclude": ["cricket"]
}
```

### Managing Saved Filters

- **View**: All your filters are listed on the Filters page
- **Delete**: Click the "Delete" button next to any filter to remove it

## Customizing Your News Feed

### User Preferences

Customize your news experience through preferences:

1. Go to your Profile page
2. Access preferences settings
3. Set your:
   - Custom feed configuration
   - Default filters
   - Timezone

### Custom Feed Configuration

Define what appears in your personalized feed:

```json
{
  "sources": ["bbc", "cnn", "reuters"],
  "categories": ["world", "technology"],
  "language": "en"
}
```

### Default Filters

Set default filters that apply automatically when browsing news:

```json
{
  "exclude": ["sports", "entertainment"],
  "minPopularity": 100
}
```

## Tips for Best Experience

### Password Security
- Use a unique password for this account
- Don't share your password with anyone
- Log out on shared devices

### Organizing Bookmarks
- Bookmark articles you want to read later
- Regularly review and remove old bookmarks
- Use descriptive saved filters for easy access

### Using Filters Effectively
- Create filters for your main interests
- Combine multiple criteria for precise results
- Update filters as your interests change

### Privacy
- Your bookmarks and filters are private
- Only you can see your saved items
- Your email is never displayed to other users

## Troubleshooting

### Can't Log In

**Problem**: Error message when trying to log in

**Solutions**:
- Check that your email and password are correct
- Ensure Caps Lock is off
- Try resetting your browser cache
- If you've made too many attempts, wait 15 minutes

### Changes Not Saving

**Problem**: Profile or preference updates don't persist

**Solutions**:
- Check your internet connection
- Try refreshing the page
- Log out and log back in
- Clear browser cache

### Missing Bookmarks

**Problem**: Can't find a bookmark you saved

**Solutions**:
- Check if you're logged into the correct account
- Verify you didn't accidentally delete it
- Try refreshing the page

## Getting Help

If you encounter issues not covered in this guide:

1. Check the [README.md](../README.md) for technical details
2. Review the [Security Documentation](./SECURITY.md) for security-related questions
3. Contact support (if available)

## Keyboard Shortcuts

Currently, the application uses standard browser shortcuts:

- **Tab**: Navigate between form fields
- **Enter**: Submit forms
- **Escape**: Close modals (if implemented)

## Mobile Usage

The application is responsive and works on mobile devices:

- Use the navigation menu to access different sections
- Forms are optimized for mobile input
- Lists are scrollable on small screens

## Privacy & Data

### What Data We Collect

- Email address (for login)
- Display name and avatar URL (optional)
- Bookmarks and saved filters
- User preferences
- Login timestamps and activity logs

### How We Use Your Data

- Authenticate you when logging in
- Personalize your news experience
- Improve the application
- Ensure security and prevent abuse

### Your Rights

- **Access**: View your profile and data anytime
- **Modify**: Update your profile and preferences
- **Delete**: Remove bookmarks and filters
- **Export**: Request a copy of your data (future feature)

### Data Security

- Passwords are securely hashed (never stored in plain text)
- Connections are encrypted
- Sessions expire after inactivity
- See [Security Documentation](./SECURITY.md) for details

## Frequently Asked Questions

### Can I change my email address?

Currently, email addresses cannot be changed. You would need to create a new account.

### How long do I stay logged in?

Your session remains active for 15 minutes of inactivity. After that, you'll need to log in again.

### Are my bookmarks backed up?

Yes, all data is stored in a secure database with regular backups.

### Can other users see my bookmarks?

No, all bookmarks and saved filters are private to your account.

### Is there a limit to how many bookmarks I can save?

There is no enforced limit, but we recommend keeping your collection manageable for best performance.

### What happens if I forget my password?

Password reset functionality will be added in a future update. Contact support for assistance.

## Future Features

Planned enhancements include:

- Password reset via email
- Email notifications for news matching your filters
- Bookmark folders and tags
- Advanced filter builder UI
- Export bookmarks and data
- Social features (optional sharing)
- Dark mode
- Mobile app
