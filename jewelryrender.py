# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/Ozbend_JewelryRender


import json
import os
import bpy
import math


class JewelryRender:

    objname = ''    # Name of current imported obj file
    obj = []    # list of current obj meshes
    cameras_1turn = []    # current working cameras list for 1 turn
    cameras_2turn = []    # current working cameras list for 1 turn

    @staticmethod
    def processobjlist(context):
        # process obj list
        __class__.clear()
        if JewelryRenderOptions.objlist:
            __class__.objname = JewelryRenderOptions.objlist.pop()
            __class__.importobj(context, __class__.objname)
            if __class__.obj:
                __class__.setmeterialstoobj(context)
                __class__.transformobj(context)
                # 1 turn (with gravi)
                __class__.cameras_1turn = JewelryRenderOptions.cameraslist.copy()
                # 2 turn (without gravi)
                if __class__.getgravimesh():
                    __class__.cameras_2turn = JewelryRenderOptions.cameraslist.copy()
                else:
                    print('Warning - no gravi mesh found', bpy.data.objects.keys())
                __class__.render(context)
            else:
                print('Error - no meshes in obj ')
                __class__.processobjlist(context)  # process next obj
        else:
            print('-- FINISHED --')


    @staticmethod
    def importobj(context, filename):
        # import current obj
        bpy.ops.object.select_all(action='DESELECT')
        rez = bpy.ops.import_scene.obj(filepath=JewelryRenderOptions.options['source_obj_dir'] + os.sep + filename, use_smooth_groups=False, use_split_groups=True)
        if rez == {'FINISHED'}:
            __class__.obj = context.selected_objects
        else:
            print('Error importing ', filename)
            __class__.processobjlist(context)   # process next obj


    @staticmethod
    def setmeterialstoobj(context):
        # set materials to current obj
        if __class__.obj:
            for mesh in __class__.obj:
                materialid = mesh.data.materials[0].name[:JewelryRenderOptions.materialidlength]
                for material in JewelryRenderOptions.materialslist:
                    if material.name[:JewelryRenderOptions.materialidlength] == materialid:
                        mesh.data.materials[0] = material

    @staticmethod
    def transformobj(context):
        # scale
        bpy.ops.transform.resize(value=(JewelryRenderOptions.options['correction']['scale']['X'],
                                        JewelryRenderOptions.options['correction']['scale']['Y'],
                                        JewelryRenderOptions.options['correction']['scale']['Z']),
                                 constraint_orientation='LOCAL')
        # translate
        bpy.ops.transform.translate(value=(JewelryRenderOptions.options['correction']['translate']['X'],
                                           JewelryRenderOptions.options['correction']['translate']['Y'],
                                           JewelryRenderOptions.options['correction']['translate']['Z']),
                                    constraint_orientation='LOCAL')
        # rotate
        bpy.ops.transform.rotate(value=JewelryRenderOptions.options['correction']['rotate']['X']*math.pi/180,
                                 axis=(1, 0, 0),
                                 constraint_orientation='LOCAL')
        bpy.ops.transform.rotate(value=JewelryRenderOptions.options['correction']['rotate']['Y']*math.pi/180,
                                 axis=(0, 1, 0),
                                 constraint_orientation='LOCAL')
        bpy.ops.transform.rotate(value=JewelryRenderOptions.options['correction']['rotate']['Z']*math.pi/180,
                                 axis=(0, 0, 1),
                                 constraint_orientation='LOCAL')
    @staticmethod
    def getgravimesh():
        gravimesh = [gravi for gravi in bpy.data.objects.keys() if JewelryRenderOptions.options['gravi_mesh_name'] in gravi]
        if gravimesh:
            return bpy.data.objects[gravimesh[0]]
        else:
            return None

    @staticmethod
    def removegravi():
        gravimesh = __class__.getgravimesh()
        if gravimesh:
            # v1 - remove the whole mesh
            # bpy.data.objects.remove(gravimesh, True)
            # for ob in __class__.obj:
            #     if JewelryRenderOptions.options['gravi_mesh_name'] in ob.name:
            #         __class__.obj.remove(ob)

            # v2 - change material - set material with texture
            gravimesh.data.materials[0] = bpy.data.materials[JewelryRenderOptions.options['gravimat']]
            # change texture to last (max name.00x number)
            gravitextures = [texture for texture in bpy.data.images.keys() if JewelryRenderOptions.options['gravitextureid'] in texture]
            lastgravitexture = sorted(gravitextures, reverse=True)[0]
            gravimesh.data.materials[0].node_tree.nodes['Gravi_text'].image = bpy.data.images[lastgravitexture]
        else:
            print('Error - no gravi mesh found to remove', bpy.data.objects.keys())

    @staticmethod
    def selectobj():
        if __class__.obj:
            for ob in __class__.obj:
                ob.select = True

    @staticmethod
    def moveobjtorendered(objname):
        # move processed obj-file to archive directory
        if os.path.exists(JewelryRenderOptions.options['rendered_obj_dir']):
            clearname = os.path.splitext(objname)[0]
            if os.path.exists(os.path.join(JewelryRenderOptions.options['source_obj_dir'], clearname + '.obj')):
                os.rename(os.path.join(JewelryRenderOptions.options['source_obj_dir'], clearname + '.obj'), os.path.join(JewelryRenderOptions.options['rendered_obj_dir'], clearname + '.obj'))
            if os.path.exists(os.path.join(JewelryRenderOptions.options['source_obj_dir'], clearname + '.mtl')):
                os.rename(os.path.join(JewelryRenderOptions.options['source_obj_dir'], clearname + '.mtl'), os.path.join(JewelryRenderOptions.options['rendered_obj_dir'], clearname + '.mtl'))
        else:
            print('Error - rendered obj directory not exists')

    @staticmethod
    def removeobj():
        # remove obj meshes from scene
        if __class__.obj:
            for ob in __class__.obj:
                bpy.data.objects.remove(ob, True)

    @staticmethod
    def render(context):
        # statrt render by cameras
        if __class__.cameras_1turn:
            context.scene.camera = __class__.cameras_1turn.pop()
            if __class__.onrenderfinished not in bpy.app.handlers.render_complete:
                bpy.app.handlers.render_complete.append(__class__.onrenderfinished)
            if __class__.onrendercancel not in bpy.app.handlers.render_cancel:
                bpy.app.handlers.render_cancel.append(__class__.onrendercancel)
            if __class__.onsceneupdate not in bpy.app.handlers.scene_update_post:
                bpy.app.handlers.scene_update_post.append(__class__.onsceneupdate)
        elif __class__.cameras_2turn:
            __class__.removegravi()
            context.scene.camera = __class__.cameras_2turn.pop()
            if __class__.onrenderfinished not in bpy.app.handlers.render_complete:
                bpy.app.handlers.render_complete.append(__class__.onrenderfinished)
            if __class__.onrendercancel not in bpy.app.handlers.render_cancel:
                bpy.app.handlers.render_cancel.append(__class__.onrendercancel)
            if __class__.onsceneupdate not in bpy.app.handlers.scene_update_post:
                bpy.app.handlers.scene_update_post.append(__class__.onsceneupdate)
        else:
            # 2 turns done - move files
            if __class__.objname:
                __class__.moveobjtorendered(__class__.objname)
            # and process next obj
            __class__.processobjlist(context)

    @staticmethod
    def clear():
        __class__.objname = ''
        if __class__.obj:
            __class__.removeobj()
        __class__.obj = []
        __class__.cameras_1turn = []
        __class__.cameras_2turn = []
        if __class__.onrenderfinished in bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.remove(__class__.onrenderfinished)
        if __class__.onrendercancel in bpy.app.handlers.render_cancel:
            bpy.app.handlers.render_cancel.remove(__class__.onrendercancel)
        if __class__.onsceneupdate in bpy.app.handlers.scene_update_post:
            bpy.app.handlers.scene_update_post.remove(__class__.onsceneupdate)
        if __class__.onsceneupdate_saverender in bpy.app.handlers.scene_update_post:
            bpy.app.handlers.scene_update_post.remove(__class__.onsceneupdate_saverender)

    @staticmethod
    def onsceneupdate(scene):
        # start next render
        if __class__.onsceneupdate in bpy.app.handlers.scene_update_post:
            bpy.app.handlers.scene_update_post.remove(__class__.onsceneupdate)
        status = bpy.ops.render.render('INVOKE_DEFAULT')
        if status == {'CANCELLED'}:
            if __class__.onsceneupdate not in bpy.app.handlers.scene_update_post:
                bpy.app.handlers.scene_update_post.append(__class__.onsceneupdate)

    @staticmethod
    def onsceneupdate_saverender(scene):
        # save render rezult on scene update
        if __class__.onsceneupdate_saverender in bpy.app.handlers.scene_update_post:
            bpy.app.handlers.scene_update_post.remove(__class__.onsceneupdate_saverender)
        __class__.saverenderrezult(scene.camera)
        # and start next render
        __class__.render(bpy.context)

    @staticmethod
    def onrenderfinished(scene):
        # save render rezult on scene update
        if __class__.onsceneupdate_saverender not in bpy.app.handlers.scene_update_post:
            bpy.app.handlers.scene_update_post.append(__class__.onsceneupdate_saverender)

    @staticmethod
    def onrendercancel(scene):
        __class__.clear()
        print('-- ABORTED BY USER --')

    @staticmethod
    def saverenderrezult(camera):
        if os.path.exists(JewelryRenderOptions.options['dest_dir']):
            path = JewelryRenderOptions.options['dest_dir'] + os.sep + os.path.splitext(__class__.objname)[0]   # dir + filename
            for mesh in __class__.obj:
                if JewelryRenderOptions.options['gravi_mesh_name'] not in mesh.name:
                    path += '_' + mesh.data.materials[0].name[:JewelryRenderOptions.materialidlength]   # + mat
            path += '_' + camera.name     # + camera
            if not __class__.getgravimesh():
                path += '_noeng'
            path += '.jpg'
            for currentarea in bpy.context.window_manager.windows[0].screen.areas:
                if currentarea.type == 'IMAGE_EDITOR':
                    overridearea = bpy.context.copy()
                    overridearea['area'] = currentarea
                    bpy.ops.image.save_as(overridearea, copy=True, filepath=path)
                    break
        else:
            print('Error - no destination directory')


class JewelryRenderOptions:

    options = None
    objlist = []    # list of filenames
    cameraslist = []
    materialslist = []
    materialidlength = 5    # identifier length (ex: MET01, GOL01)

    @staticmethod
    def readfromfile(dir):
        with open(dir + os.sep + 'options.json') as currentFile:
            __class__.options = json.load(currentFile)
