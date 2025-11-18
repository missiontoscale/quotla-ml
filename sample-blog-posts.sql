-- Sample Blog Posts for Testing
-- Run this AFTER you've created your first admin user

-- Sample Post 1: Getting Started with Quotla
INSERT INTO blog_posts (title, slug, excerpt, content, published, published_at)
VALUES (
  'Getting Started with Quotla',
  'getting-started-with-quotla',
  'Learn how to set up your business profile and create your first professional quote in minutes.',
  '<h2>Welcome to Quotla!</h2>
<p>Quotla is your all-in-one solution for creating professional quotes and invoices. This guide will walk you through the essential steps to get started.</p>

<h3>Step 1: Set Up Your Business Profile</h3>
<p>Navigate to <strong>Settings</strong> from the dashboard menu. Here you can:</p>
<ul>
  <li>Upload your company logo</li>
  <li>Add your business information</li>
  <li>Set your default currency</li>
  <li>Configure tax settings</li>
</ul>

<h3>Step 2: Add Your First Client</h3>
<p>Go to <strong>Clients</strong> and click "Add Client". Fill in your client''s contact information including:</p>
<ul>
  <li>Name and company details</li>
  <li>Email and phone number</li>
  <li>Billing address</li>
</ul>

<h3>Step 3: Create Your First Quote</h3>
<p>Click on <strong>Quotes</strong> and then "Create Quote". Add line items, use AI to generate professional descriptions, and send it to your client!</p>

<p>That''s it! You''re ready to start managing your business documents professionally.</p>',
  TRUE,
  NOW()
);

-- Sample Post 2: AI-Powered Descriptions
INSERT INTO blog_posts (title, slug, excerpt, content, published, published_at)
VALUES (
  'How to Use AI-Powered Description Generation',
  'ai-powered-description-generation',
  'Discover how Quotla''s AI feature can help you write professional service descriptions in seconds.',
  '<h2>AI-Powered Descriptions</h2>
<p>One of Quotla''s most powerful features is AI-powered content generation. Let''s explore how to use it effectively.</p>

<h3>What is AI Description Generation?</h3>
<p>When creating quotes or invoices, you can use AI to automatically generate professional descriptions for your services. Simply describe what you''re offering in plain language, and AI transforms it into polished, client-ready text.</p>

<h3>How to Use It</h3>
<ol>
  <li>When adding a line item to a quote or invoice, click the <strong>"Generate with AI"</strong> button</li>
  <li>Describe your service in simple terms (e.g., "Website design with 5 pages and contact form")</li>
  <li>Click "Generate" and watch AI create a professional description</li>
  <li>Review and edit if needed, then add to your document</li>
</ol>

<h3>Tips for Best Results</h3>
<ul>
  <li>Be specific about what you''re offering</li>
  <li>Include key features or deliverables</li>
  <li>Mention any special requirements</li>
  <li>You can always edit the AI-generated text</li>
</ul>

<p>AI description generation saves time while ensuring your quotes look professional and detailed.</p>',
  TRUE,
  NOW()
);

-- Sample Post 3: Best Practices
INSERT INTO blog_posts (title, slug, excerpt, content, published, published_at)
VALUES (
  '5 Best Practices for Professional Quotes',
  'best-practices-professional-quotes',
  'Follow these tips to create quotes that win more clients and get approved faster.',
  '<h2>5 Best Practices for Professional Quotes</h2>
<p>Creating winning quotes is an art. Here are five best practices to improve your quote acceptance rate.</p>

<h3>1. Be Clear and Detailed</h3>
<p>Ambiguity is the enemy of approval. Clearly describe each service or product, including:</p>
<ul>
  <li>What''s included</li>
  <li>Timeline or delivery schedule</li>
  <li>Any limitations or exclusions</li>
</ul>

<h3>2. Professional Presentation Matters</h3>
<p>Use your company logo, maintain consistent formatting, and ensure there are no typos. Quotla makes this easy with professional templates.</p>

<h3>3. Set Clear Validity Dates</h3>
<p>Always include a validity period for your quote. This creates urgency and protects you from price changes.</p>

<h3>4. Include Payment Terms</h3>
<p>Specify when and how you expect to be paid. Common terms include:</p>
<ul>
  <li>50% upfront, 50% on completion</li>
  <li>Net 30 days</li>
  <li>Upon project milestones</li>
</ul>

<h3>5. Follow Up Promptly</h3>
<p>After sending a quote, follow up within 2-3 business days. Use Quotla''s dashboard to track which quotes are pending and need attention.</p>

<p>Implementing these practices will help you create quotes that clients trust and approve quickly.</p>',
  TRUE,
  NOW()
);

-- Sample Draft Post (unpublished)
INSERT INTO blog_posts (title, slug, excerpt, content, published, published_at)
VALUES (
  'Understanding Multi-Currency Support',
  'understanding-multi-currency-support',
  'A comprehensive guide to working with international clients using Quotla''s multi-currency features.',
  '<h2>Multi-Currency Support</h2>
<p>This is a draft post about multi-currency support. Content coming soon...</p>',
  FALSE,
  NULL
);
