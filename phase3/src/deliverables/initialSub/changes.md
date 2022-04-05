1. Changes in Catalog
    1. Structure of Horzontal_Fragments changed
    1. Structure of Derived_Horizontal_Fragments changed
1. Changes in Fragmentation
    1. Order_Items table is now fragmented too
    1. It is derived horizontally fragmented using the horizonatal fragments of Food_Items table
    1. Subsequently Order table is derived horizontally fragmented using fragments of Order_Items table
1. The corresponding changes to allocation table has also been made.
    1. Well not changes to be exact.
    1. Structure is still the same.
    1. But new entries for the new made fragments are added.