# Notice

The furniture models and textures come from [Paladin's Furniture](https://github.com/UnlikePaladin/paladins-furniture) by UnlikePaladin, under the GNU Lesser General Public License v3.0 in [LICENSE](LICENSE). The LGPL builds on the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html).

The pieces in `resources/pfm` were taken from commit [01ec5d7](https://github.com/UnlikePaladin/paladins-furniture/tree/01ec5d7a3269086cd2c07ffe58aff166416b3bf3) of 16 June 2026. On 24 June 2026 Paladin's Furniture moved its models and textures to the PolyForm Shield licence, so nothing from later commits is used here.

`tools/import_pfm.py` changed them: each Java model has its parent models merged in and its Paladin textures moved under `cutebear_furniture:block/pfm/`, pieces built from several of Paladin's part models have them merged into one, and the Bedrock geometry and texture atlases are generated from the Java models. The bed mattresses are rebuilt on Minecraft's bed textures. The textures in `resources/pfm/textures` are unchanged copies, apart from `lamp_shade_<colour>.png`, `office_chair/office_chair_back_<colour>.png` and `office_chair/office_chair_seat_<colour>.png`, which are tinted with that dye colour.
