import bpy, imp

from easyGame import easyMaterial
from easyGame import easyAsset

imp.reload(easyMaterial)
imp.reload(easyAsset)


bl_info = {
	"name": "Easy Game Collection",
	"author": "Mike Pan",
	"version": (1, 2),
	"blender": (2, 70, 0),
	"location": "View3D > Tool Shelf > Easy Tabs",
	"description": "Help make the game-creation process simpler.",
	"warning": "",
	"wiki_url": "",
	"category": "Game Engine"
}



def register():
	bpy.utils.register_class(BLEasyMaterial)
	bpy.utils.register_class(BLEasyMaterialAdv)
	bpy.utils.register_class(BLEasyAsset)
	# bpy.utils.register_class(BLSettings)
	bpy.utils.register_class(BLEasyMaterialCreate)
	bpy.utils.register_class(BLEasyAssetCreate)


def unregister():
	bpy.utils.unregister_class(BLEasyMaterial)
	bpy.utils.unregister_class(BLEasyMaterialAdv)
	bpy.utils.unregister_class(BLEasyAsset)
	# bpy.utils.unregister_class(BLSettings)
	bpy.utils.unregister_class(BLEasyMaterialCreate)
	bpy.utils.unregister_class(BLEasyAssetCreate)



###############################################################################


class GamePanel():
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'

	
class BLEasyMaterial(GamePanel, bpy.types.Panel):
	"""Creates the EasyMaterial UI"""
	bl_label = "Easy Material"
	bl_category = "Easy Material"

	def draw(self, context):
		layout = self.layout
		obj = context.object

		# bail on wrong display mode
		if context.scene.game_settings.material_mode != 'GLSL':
			row = layout.row()
			row.label('EasyMaterial requires GLSL mode', icon='ERROR')
			row = layout.row()
			row.prop(context.scene.game_settings, 'material_mode', text='')
			return

		# bail on no object (We don't want to use poll because that hides the panel)
		if not obj:
			return

		# material datablock manager
		row = layout.row()
		layout.template_ID_preview(obj, "active_material", new="easy.matcreate")

		# material editor
		row = layout.row()
		for materialSlot in context.active_object.material_slots:
			mat = materialSlot.material

			# bail code
			if not mat:
				continue
			if 'uberMaterial' not in mat:
				row.label('Not an UberMaterial', icon='ERROR')
				continue

			# edit albedo
			row = layout.row()
			row.prop(mat, 'diffuse_intensity', text='Albedo')

			metallicTextureSlot = None
			for textureSlot in mat.texture_slots:
				if textureSlot:
					# bail code
					if textureSlot.use_map_color_spec and textureSlot.blend_type == 'COLOR':
						continue

					tex = textureSlot.texture
					text = tex.name.split('.')[-1]
					if text.isnumeric():
						text = tex.name.split('.')[-2]

					# move to advanced section
					if text in ['Emit', 'Alpha']:
						continue						

					row = layout.row()
					# enable/disable texture channel
					split  = layout.split(percentage=0.20)
					row = split.row()
					row.prop(textureSlot, 'use', text=text)

					# image browse control
					row = split.row()
					row.active = textureSlot.use
					row.template_ID(tex, "image", open="image.open")
					split  = layout.split(percentage=0.20)

					# empty
					row = split.row()

					split.active = textureSlot.use
					# additional properties
					if text == 'Col':
						split.prop(textureSlot, 'diffuse_color_factor', text='Factor')
						split.prop(mat, 'diffuse_color', text='')
					if text == 'Nor':
						split.prop(textureSlot, 'normal_factor', text='Factor')
					if text == 'Gloss':
						split.prop(textureSlot, 'default_value', text='Factor')

					if textureSlot.texture_coords == 'UV' and tex.image:
						split.prop_search(textureSlot, "uv_layer", context.active_object.data, "uv_textures", text="")


class BLEasyMaterialAdv(GamePanel, bpy.types.Panel):
	"""Creates the EasyMaterial UI"""
	bl_label = "Advanced"
	bl_category = "Easy Material"

	@classmethod
	def poll(cls, context):
		return context.active_object

	def draw(self, context):
		layout = self.layout
		obj = context.object

		# bail on no mat slot
		if not context.active_object.material_slots:
			return

		# material editor
		row = layout.row()
		for materialSlot in context.active_object.material_slots:
			mat = materialSlot.material

			# bail code
			if not mat:
				continue

			if 'uberMaterial' not in mat:
				# row.label('Not an UberMaterial', icon='ERROR')
				continue

			row.prop(mat, 'use_transparency', 'Transparent')
			if mat.use_transparency:
				row.prop(mat, 'transparency_method', expand=True)

			for textureSlot in mat.texture_slots:
				if textureSlot:

					# bail code
					if textureSlot.use_map_color_spec and textureSlot.blend_type == 'COLOR':
						row.prop(textureSlot, 'use', text='Metallic (Use color from Gloss map as Spec Color)')
						continue

					row = layout.row()
					tex = textureSlot.texture
					text = tex.name.split('.')[-1]
					if text.isnumeric():
						text = tex.name.split('.')[-2]

					if text not in ['Emit', 'Alpha']:
						continue

					# enable/disable texture channel
					split  = layout.split(percentage=0.20)
					split.prop(textureSlot, 'use', text=text)

					# image browse control
					split.template_ID(tex, "image", open="image.open")
					split  = layout.split(percentage=0.20)

					# empty
					row = split.row()

					# additional properties
					if text == 'Emit':
						split.prop(textureSlot, 'emit_factor', text='Factor')

					if textureSlot.texture_coords == 'UV' and tex.image:
						split.prop_search(textureSlot, "uv_layer", context.active_object.data, "uv_textures", text="")

	
class BLEasyAsset(GamePanel, bpy.types.Panel):
	"""Creates The Easy Asset Interface"""
	bl_label = "Easy Asset"
	bl_context = "objectmode"
	bl_category = "Easy Asset"

	def draw(self, context):
		layout = self.layout
		obj = context.object

		row = layout.row()
		row.label('Create Camera')
		row = layout.row(align=True)
		row.operator("easy.assetcreate", text='FPS Camera').arg = 'camera.fps'
		row.operator("easy.assetcreate", text='Orbit Camera').arg = 'camera.orbit'

		row = layout.row()
		row.label('Create Lights')
		row = layout.row(align=True)
		row.operator("easy.assetcreate", text='Day-Night Cycle').arg = 'light.cycle'
		row.operator("easy.assetcreate", text='Soft Light').arg = 'light.soft'
		row = layout.row()

		row.label('Create Objects')
		col = layout.column(align=True)
		col.operator("easy.assetcreate", text='Barrel-Wood').arg = 'barrel.BarrelWood'
		col.operator("easy.assetcreate", text='Barrel-Wood-Faded').arg = 'barrel.BarrelWood2'
		col.operator("easy.assetcreate", text='Barrel-Blue').arg = 'barrel.BarrelOilBlue'
		col.operator("easy.assetcreate", text='Barrel-Red').arg = 'barrel.BarrelOilRed'
		col.operator("easy.assetcreate", text='Barrel-Red-Yellow').arg = 'barrel.BarrelOilRed2'
		col.operator("easy.assetcreate", text='Barrel-Galvanized').arg = 'barrel.BarrelOilGalvanized'

		col = layout.column(align=True)
		col.operator("easy.assetcreate", text='Concrete-Divider').arg = 'concrete.ConcreteDivider'
		col.operator("easy.assetcreate", text='Concrete-Block1').arg = 'concrete.ConcreteBlock1'
		col.operator("easy.assetcreate", text='Concrete-Block2').arg = 'concrete.ConcreteBlock2'
		col.operator("easy.assetcreate", text='Concrete-Block3').arg = 'concrete.ConcreteBlock3'
		row = layout.row()

		row.label('Effects')
		col = layout.column(align=True)
		col.operator("easy.assetcreate", text='Plane Mirror').arg = 'fx.mirror'
		row = layout.row()
		row.operator("easy.assetcreate", text='Post-Processing 2D Filters').arg = 'fx.2DFilter'

		col = layout.column(align=True)
		col.operator("easy.assetcreate", text='Particles - Smoke').arg = 'fx.emitterSmoke'
		col.operator("easy.assetcreate", text='Particles - Spark').arg = 'fx.emitterSpark'
		col.operator("easy.assetcreate", text='Particles - Snow').arg = 'fx.emitterSnow'


		row = layout.row()
		
		# row.label('Assets:')
		# template_list now takes two new args.
		# The first one is the identifier of the registered UIList to use (if you want only the default list,
		# with no custom draw code, use "UI_UL_list").
		# layout.template_list("UI_UL_list", "assetid", obj, "material_slots", obj, "active_material_index")



class BLEasyMaterialCreate(bpy.types.Operator):
	"""Create an übershader"""
	bl_label = "New UberMaterial"
	bl_idname = 'easy.matcreate'
	bl_options = {'REGISTER', 'UNDO'}

	MatName = bpy.props.StringProperty(name='Material Name', default='uber')

	def execute(self, context):
		if error := easyMaterial.sanityCheck(context):
			self.report({'ERROR'}, error)
			return {'CANCELLED'}
		else:
			mat = easyMaterial.createMaterial(context, self.MatName)
			easyMaterial.assignMaterial(context, mat)
			return {'FINISHED'}


class BLEasyAssetCreate(bpy.types.Operator):
	"""Create an asset"""
	bl_label = "New Asset"
	bl_idname = 'easy.assetcreate'
	bl_options = {'REGISTER', 'UNDO'}

	arg = bpy.props.StringProperty()
	
	def execute(self, context):

		objType, option = self.arg.split('.')

		# cleanup before we start
		bpy.ops.object.select_all(action='DESELECT')

		if objType == 'camera':
			obj = easyAsset.createCamera(option)
		elif objType == 'light':
			obj = easyAsset.createLight(option)
		elif objType == 'fx':
			obj = easyAsset.createFX(option)
		elif objType == 'barrel':
			obj = easyAsset.createBarrel(option)
		elif objType == 'concrete':
			obj = easyAsset.createConcrete(option)
		else:
			obj = 'Sorry, not implemented yet.'

		if not obj:
			self.report({'ERROR'}, 'something went wrong')
			return {'CANCELLED'}
		else:

			obj.select = True
			bpy.context.scene.objects.active = obj

			return {'FINISHED'}
		

