3dlife
======

An implementation of the game of life that operates on Wavefront .OBJ 
files. The point of this is to simulate reaction diffusion in 
morphogenesis and attempt to make a (more-or-less) educated guess at 
what sort of markings people would have if we were marked like, say, 
tigers. 

The practical applications are limiteless! Limitless, I say!

This is a bunch of files related to an attempt to create a version of the game of life, 
or a reaction diffusion model of morphogenesis, to create a pattern like what you would
get if the functions which create stripes on zebras and tigers or spots on leopards were
to operate on a human shape. 

There are a few conceptual bugs with this, not least of which is that tigers are born 
with stripes, but not as full-sized tigers, so you can't really seperate the pattern
generation from maturation and the attendant shape changes. 

Another is that no one really has a solid handle on the rules that lead to tiger stripes, 
and it's probably more complex than reaction diffusion. 

Finally, there's also the problem that surface polys are not the same as cells. There are
bigger polys where there is less curvature and more where there is more curvature. A
method of breaking up a surface poly based on voroni diagrams or something can compensate 
for this to create an even distribution of surface polys. 

The program arose from a description with a couple of tattoo enthusiasts, who commented
that animal-inspired patterns always looked "applied" rather than natural on people. I 
am attempting to fix that with this program. 

The rocket.obj, .mtl, and .png files are from Processing, I was using them as examples. 

It seems like the way to do per-face color is to have a texture that has a region of 
each color, and use the texture verticies of each face to select a region of the texture
that is the appropriate color. 

The generation method for this texture would be to determine the largest region of each 
color that will be needed, and then index all of the others inside of it. During 
generation, each face will be marked with the appropriate calculated color, and the 
texture will then be rendered based on the final state of the generated form. 

The rocket file is multiple groups (g tag in .obj) file. This is a problem for the
life-style calculation because there's no clear way to have adjacency across the gaps. 
