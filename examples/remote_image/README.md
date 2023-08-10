# Remote Image

This is the simplest possible example, rather than building an image as part of deployment, it uses an existing image.

This provides two things:

- Coverage that the infrastructure can handle images not from the registry where custom images are pushed.
- Coverage of deployment independently of the image pushing step.
