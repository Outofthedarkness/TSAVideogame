from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.showbase.DirectObject import DirectObject
from direct.controls.InputState import InputState
from panda3d.core import CollisionTraverser, Plane, Vec3, CollisionPlane, CardMaker, AmbientLight, PointLight, CollisionRay, BitMask32, CollisionHandlerQueue, CollisionHandlerEvent, CollisionNode, CollisionHandlerPusher, CollisionBox, Point3, CollisionSphere, LVector3, CollisionPolygon, WindowProperties
from panda3d.ai import AIWorld, AICharacter
import direct.gui.DirectGuiGlobals as DGG
from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.showbase.Transitions import Transitions

#loadPrcFileData("", "texture-minfilter linear-mipmap-linear")

class CameraControllerBehaviour(DirectObject):
    _instances = 0
    def __init__(self, camera, velocity=9, mouse_sensitivity=0.2, initial_pos=(-0.5, -12, 7.7), showbase=None):
        self._camera = camera
        self._velocity = velocity
        self._mouse_sensitivity = mouse_sensitivity
        self._keys = None
        self._input_state = InputState()
        self._heading = 0.0
        self._pitch = 0.0
        self._yaw = 0.0
        self._roll = 0.0
        self._showbase = base if showbase is None else showbase
        self._gravity = LVector3(0, 0, -3.8)  # Set gravity vector pointing downward
        self._instance = CameraControllerBehaviour._instances
        CameraControllerBehaviour._instances += 1
        self._camera.setPos(*initial_pos)
        # Set the initial position of the camera

    def setup(self, keys={
        'w':"forward", 
        's':"backward",
        'a':"left",
        'd':"right",
        'space':"up",
        'e':"down"
    }):
        self._keys = keys
        for key in self._keys:
            self._input_state.watchWithModifiers(self._keys[key], key)

        self._showbase.disableMouse()

        props = WindowProperties()
        props.setCursorHidden(True)

        self._showbase.win.requestProperties(props)

        self._showbase.taskMgr.add(self.update, "UpdateCameraTask" + str(self._instance))
    
    def destroy(self):
        self.disable()
        self._input_state.delete()

        del self

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, velocity):
        self._velocity = velocity
    
    @property
    def mouse_sensitivity(self):
        return self._mouse_sensitivity

    @mouse_sensitivity.setter
    def mouse_sensitivity(self, sensitivity):
        self._mouse_sensitivity = sensitivity

    def disable(self):
        self._showbase.taskMgr.remove("UpdateCameraTask" + str(self._instance))

        props = WindowProperties()
        props.setCursorHidden(False)

        self._showbase.win.requestProperties(props)            

    def update(self, task):
        dt = globalClock.getDt()
        
        # Get mouse movement for rotation
        md = self._showbase.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        center_x = self._showbase.win.getXSize() // 2
        center_y = self._showbase.win.getYSize() // 2

        if self._showbase.win.movePointer(0, center_x, center_y):
            self._yaw = self._yaw - (x - center_x) * self._mouse_sensitivity
            self._pitch = self._pitch - (y - center_y) * self._mouse_sensitivity

        # Clamp the pitch to prevent camera flipping over
        self._pitch = max(-89, min(89, self._pitch))
        
        # Set the camera's orientation
        self._showbase.camera.setHpr(self._yaw, self._pitch, self._roll)
        
        # Access the camera's lens and set the focal length
        lens = self._showbase.cam.node().getLens()
        lens.setFocalLength(0.25)
        
        # Get the camera's position
        
        # Calculate the position increment
        pos_increment = self._velocity * dt
        
        # Handle keyboard input for movement
        if  self._input_state.isSet('forward'):
            self._showbase.camera.setY(self._showbase.camera, pos_increment)

        if  self._input_state.isSet('backward'):
            self._showbase.camera.setY(self._showbase.camera, -pos_increment)

        if  self._input_state.isSet('left'):
            self._showbase.camera.setX(self._showbase.camera, -pos_increment)

        if  self._input_state.isSet('right'):
            self._showbase.camera.setX(self._showbase.camera, pos_increment)

        if  self._input_state.isSet('up'):
            self._showbase.camera.setZ(self._showbase.camera, pos_increment)

        if  self._input_state.isSet('down'):
            self._showbase.camera.setZ(self._showbase.camera, -pos_increment)
        
        self.cam_pos = self._showbase.camera.getPos(self._showbase.render)
        # Apply gravity to the camera's position
        (self.cam_pos) += self._gravity * dt
        
        # Update the camera's position
        self._showbase.camera.setPos(self.cam_pos)
        return Task.cont
class MyApp(ShowBase):
    password = ""
    bossspawned = False
    finalbosscollison = None
    safepadopen = False
    onebutton = '**removed**'
    haskey = False
    won = False
    def movieplay(self, task):
        if task.time < 7:
            return Task.cont
        self.card.removeNode()
        return Task.done
    def tutorial(self, task):
        if task.time < 1:
            return Task.cont
        self.tutorialine1.destroy()
        self.tutorialine2.destroy()
        self.tutorialine3.destroy()
        self.tutorialine4.destroy()
        self.tutorialine5.destroy()
        self.tutorialine6.destroy()
        self.cam_controller = CameraControllerBehaviour(self.camera, velocity=9, mouse_sensitivity=.02)
        self.cam_controller.setup(keys={'w':"forward",
            's':"backward",
            'a':"left",
            'd':"right",
            'space':"up",
            'e':"down"})
        self.set()
        self.spawnateachdoor(1)
        self.start = False
        return Task.done
    def finalboss(self):
        movietex = self.loader.loadTexture(r"models/cutscene.avi")
        self.cm = CardMaker("card")
        self.cm.setFrameFullscreenQuad()
        self.cm.setUvRange(movietex)
        self.card = self.render2d.attachNewNode(self.cm.generate())
        self.card.setTexture(movietex)
        self.card.setPos(0, 0, 0)
        taskMgr.add(self.movieplay, "movieplay")
        self.bosshealth = 100
        self.bossspawned = True
        self.bosshealthbar = DirectWaitBar(text="Boss HP", value=100, pos=(0, -15, .6))
        self.finalmodel = self.loader.loadModel(r"models/Ghoooooost.glb")
        self.finalmodel.reparentTo(self.render)
        self.finalmodel.setScale(10)
        self.finalmodel.setPos(0, 0, 17)
        self.finalmodel.setHpr(0, 90, 90)
        self.finalbosscollison = CollisionNode("finalbosscollison")
        self.finalbosscollison.addSolid(CollisionSphere(0, 0, 0, .3))
        self.finalbosscollisonpath = self.finalmodel.attachNewNode(self.finalbosscollison)
        self.cTrav.addCollider(self.finalbosscollisonpath, self.npcintocam)
        self.bossaimodel = self.loader.loadModel(r"models/aidotupdater.glb")
        self.finalbossaicharacter = AICharacter("finalboss", self.bossaimodel, 100, .1, 5)
        self.Aiworld.addAiChar(self.finalbossaicharacter)
        self.finalbossbehaviour = self.finalbossaicharacter.getAiBehaviors()
        self.finalbossbehaviour.pursue(self.camera)
        self.finalbossbehaviour.arrival(2)
    def keyposupdate(self, task):
        
        camera_forward = self.camera.getQuat(self.render).getForward()
        camera_up = self.camera.getQuat(self.render).getUp()
        camera_left = self.camera.getQuat(self.render).getRight()
        camera_position = self.camera.getPos(self.render)
        key_position = (
            camera_position +
            camera_forward * 1.5 -  # Forward by 1.0 units
            camera_up * 0.5 +       # Downward by 0.5 units
            camera_left * -0.4      # Rightward by 0.3 units
        )
        self.keymodel.setPos(key_position)
        self.keymodel.setHpr(self.camera.getH(), 60, 10)  
        return Task.cont
    def safenumpad(self):
        self.safepadopen = True
        self.cam_controller.disable()
        self.keymodel = self.loader.loadModel(r"models/key.glb")
        self.keyimage = ()
        self.password = ""
        def setnumber1():
            self.password += "1"
        def setnumber2():
            self.password += "2"
        def setnumber3():
            self.password += "3"
        def setnumber4():
            self.password += "4"
        def setnumber5():
            self.password += "5"
        def setnumber6():
            self.password += "6"
        def setnumber7():
            self.password += "7"
        def setnumber8():
            self.password += "8"
        def setnumber9():
            self.password += "9"
        def setnumber0():
            self.password += "0"
        def clearpassword():
            self.password = ""     
        self.onebutton = DirectButton(text=("1", "1", "1", "disabled"), scale=.2, command=setnumber1, pos = (-.45, -10, .3))
        self.twobutton = DirectButton(text=("2", "2", "2", "disabled"), scale=.2, command=setnumber2, pos = (-.05, -10, .3))
        self.threebutton = DirectButton(text=("3", "3", "3", "disabled"), scale=.2, command=setnumber3, pos = (.35, -10, .3))
        self.fourbutton = DirectButton(text=("4", "4", "4", "disabled"), scale=.2, command=setnumber4, pos = (-.45, -10, 0))
        self.fivebutton = DirectButton(text=("5", "5", "5", "disabled"), scale=.2, command=setnumber5, pos = (-.05, -10, 0))
        self.sixbutton = DirectButton(text=("6", "6", "6", "disabled"), scale=.2, command=setnumber6, pos = (.35, -10, 0))
        self.sevenbutton = DirectButton(text=("7", "7", "7", "disabled"), scale=.2, command=setnumber7, pos = (-.45, -10, -.3))
        self.eightbutton = DirectButton(text=("8", "8", "8", "disabled"), scale=.2, command=setnumber8, pos = (-.05, -10, -.3))
        self.ninebutton = DirectButton(text=("9", "9", "9", "disabled"), scale=.2, command=setnumber9, pos = (.35, -10, -.3))
        self.zerobutton = DirectButton(text=("0", "0", "0", "disabled"), scale=.2, command=setnumber0, pos = (-.05, -10, -.6))
        self.clearbutton = DirectButton(text=("clear", "clear", "clear", "disabled"), scale=.1, command=clearpassword, pos = (-.45, -10, -.6))
        def checkpassword():
            if self.password == "0717":
                self.keymodel = self.loader.loadModel(r"models/key.glb")
                self.keyimage = OnscreenImage(image = r"models/key.png", pos = (-.8, 0, .8), scale = (.1, .1, .1))
                self.haskey = True
                self.keyimage.setTransparency(True)
                self.keymodel.reparentTo(self.render)
                self.keymodel.setScale(4)
                self.cam_controller.setup()
                self.onebutton.destroy()
                self.twobutton.destroy()
                self.threebutton.destroy()
                self.fourbutton.destroy()
                self.fivebutton.destroy()
                self.sixbutton.destroy()
                self.sevenbutton.destroy()
                self.eightbutton.destroy()
                self.ninebutton.destroy()
                self.zerobutton.destroy()
                self.clearbutton.destroy()
                self.enterbutton.destroy()
                self.onebutton = '**removed**'
                taskMgr.add(self.keyposupdate, "keyposupdate")
                print("Password Correct")
        self.enterbutton = DirectButton(text=("enter", "enter", "enter", "disabled"), scale=.1, command=checkpassword, pos = (.35, -10, -.6))
    def manaupdate(self, task):
        self.manaamount = self.manaamount + .04
        self.manabar['value'] = self.manaamount
        if self.healthpoints < 100:
            self.healthpoints = self.healthpoints + .01
        else:
            self.healthpoints = 100
        return Task.cont
    def death(self):    
        transitions = Transitions(loader=self.render)
        transitions.fadeOut(t=1)
        transitions.fadeIn(t=1)
        Deathscreen = OnscreenImage(image="models/deathscreen.jpg", scale=(2, 1, 1), pos=(0, 0, 0))
        self.cam_controller.disable()
        self.crosshair.destroy()
        def reset():
            Deathscreen.destroy()
            respawnbutton.destroy()
            npctoremove = []
            for npc in self.npcs:
                if not self.npcs[npc].isEmpty():
                    npctoremove.append(npc)
            for npc in npctoremove:
                self.npcs[npc].removeNode()
                del self.npcs[npc]
            self.died = False
            self.healthpoints = 100
            self.crosshair = OnscreenImage(
                image="models/crosshair.png",  # Replace with your crosshair image path
                pos=(0, 0, 0),  # Center of the screen
                scale=0.05       # Adjust scale for size
            )
            self.crosshair.setTransparency(True)
            self.cam_controller.setup()
            self.camera.setPos(0, -18, 14)
        respawnbutton = DirectButton(text=("respawn", "fine", "do you really?", "disabled"),
            scale=.1, command=reset, pos = (0, -10, -.8))           
    def spawnateachdoor(self, num_npcs):
        self.spawnnpcs(num_npcs*4, 14, -49)
    def click(self):
        # Create a CollisionRay for the wand
        props = self.win.getProperties()
        if not props.getForeground() or not props.getCursorHidden() or props.getMouseMode() != WindowProperties.MRelative:
            self.win.requestProperties(WindowProperties(foreground=True, mouse_mode=WindowProperties.MRelative, cursor_hidden=True))
        ray_node = CollisionNode('wand-ray')
        ray = CollisionRay()
        ray.setOrigin(0, 0, 0)  # Start at the camera
        ray.setDirection(0, 1, 0)  # Point forward
        ray_node.addSolid(ray)

        ray_path = self.camera.attachNewNode(ray_node)
        ray_node.setFromCollideMask(BitMask32.bit(0))
        ray_node.setIntoCollideMask(BitMask32.allOff())

        collision_queue = CollisionHandlerQueue()
        self.cTrav.addCollider(ray_path, collision_queue)

        # Perform collision traversal
        self.cTrav.traverse(self.render)

        try:
            # Process collisions
            num_collisions = collision_queue.getNumEntries()

            if num_collisions > 1:
                collision_queue.sortEntries()
                entry = collision_queue.getEntry(1)  # Get the closest collision
                hit_node = entry.getIntoNode()
                for hits in collision_queue.getEntries():
                    if hits.getIntoNode() == self.safe_node and self.safepadopen == False:
                        print("safe")
                        self.safenumpad()
                if hit_node == self.upstairdoor_collision_node and self.haskey == True:
                    taskMgr.remove("keyposupdate")
                    self.keymodel.removeNode()
                    self.upstairdoor_collision_node.removeSolid(0)
                    self.finalboss()
                for hits in collision_queue.getEntries():
                    if hits.getIntoNode() == self.finalbosscollison and self.bossspawned == True:
                        print("boss")
                        self.bosshealth -= 3
                # Find the ghost that was hit
                ghosts_to_remove = []  # Queue for ghosts to remove
                for ghost_name, ghost in self.npcs.items():
                    ghost_node = ghost.find("**/+CollisionNode")
                    if not ghost_node.isEmpty() and ghost_node.node() == hit_node:
                        if not ghost.isEmpty():
                            ghosts_to_remove.append(ghost_name)

                # Remove ghosts after processing collisions
                if self.manaamount > 0:
                    for ghost_name in ghosts_to_remove:
                        if ghost_name in self.npcs:
                            self.npchealths[ghost_name] -= 1
                            print(f"{ghost_name} hit!")
                            self.manaamount -= 3

        except AssertionError as e:
            print("AssertionError occurred during collision processing.")
            print(e)
        except KeyError as e:
            print("KeyError occurred during collision processing.")
            pass
        # Cleanup
        self.cTrav.removeCollider(ray_path)  # Remove collider from traverser
        ray_path.removeNode()  # Safely remove the ray
        collision_queue.clearEntries()  # Clear the queue
    def spawnnpcs(self, num_npcs, posx, posy):
        for a in range(num_npcs):
            i = self.i
            self.i += 1
            npc_name = f"npc{i}"
            aidotname = f"aidot{i}"
            aicharname = f"aichar{i}"
            aicharbehaviorname = f"aibehavior{i}"
            collidername = f"collider{i}"
            self.npchealths[npc_name] = 3
            self.npcs[npc_name] = self.loader.loadModel(r"models/newghost.glb")
            self.aidotdict[aidotname] = self.loader.loadModel(r'models/aidotupdater.glb')
            self.aidotdict[aidotname].reparentTo(self.render)
            self.npcs[npc_name].reparentTo(self.render)
            self.npcs[npc_name].setPos(posx+i, posy+i, 10)
            self.aidotdict[aidotname].setPos(posx+i, posy+i, 10)
            self.npcs[npc_name].lookAt(self.camera)
            self.npcs[npc_name].setHpr(0,90,0)
            self.npcs[npc_name].setScale(2,2,2)
            self.colliderdict[collidername] = CollisionNode(npc_name)
            self.colliderdict[collidername].addSolid(CollisionSphere(0, 0, 0, 1))
            self.Aichardict[aicharname] = AICharacter(f"npc{i}", self.aidotdict[aidotname], 100, 0.05, 5)
            self.Aiworld.addAiChar(self.Aichardict[aicharname])
            self.Aicharbehaviorsdict[aicharbehaviorname] = self.Aichardict[aicharname].getAiBehaviors()
            self.Aicharbehaviorsdict[aicharbehaviorname].pursue(self.camera)
            self.Aicharbehaviorsdict[aicharbehaviorname].arrival(7) #arrival
            self.npcColliderpath = self.npcs[npc_name].attachNewNode(self.colliderdict[collidername])
        self.i = 0
        self.cTrav.addCollider(self.npcColliderpath, self.npcintocam)
    def loadmodels(self):
        self.npcs = {}
        self.aidotdict = {}
        self.Aichardict = {}
        self.Aicharbehaviorsdict = {}
        self.colliderdict = {}
        self.npchealths = {}
        self.healthpoints=100
        self.manaamount=100
        self.bar = DirectWaitBar(text="HP", value=100, pos=(-.5, -15, -.8))
        self.bar['barColor'] = (0, 2, 0, 2)
        self.bar['text_scale'] = .05
        self.bar['frameSize'] = (-.5, .5, -.035, .02)
        self.bar['barRelief']= DGG.SUNKEN
        self.manabar = DirectWaitBar(text="Mana", value=100, pos=(-.5, -15, -.9))
        self.manabar['barColor'] = (0, 9, 2, 2)
        self.manabar['text_scale'] = .05
        self.manabar['frameSize'] = (-.5, .5, -.035, .02)
        self.manabar['barRelief']= DGG.SUNKEN
        # Crosshair setup
        self.crosshair = OnscreenImage(
            image="models/crosshair.png",  # Replace with your crosshair image path
            pos=(0, 0, 0),  # Center of the screen
            scale=0.05       # Adjust scale for size
        )
        self.plight = PointLight('dlight')
        self.plnp = self.camera.attachNewNode(self.plight)
        self.render.setLight(self.plnp)
        self.plight.setColor((10, 10, 10, 10))
        self.plight.attenuation = (1, .5, 0)
        self.crosshair.setTransparency(True) 
        self.Manor = self.loader.loadModel(r"models/HauntedMan.glb")
        self.Manor.reparentTo(self.render)
        self.Manor.setHpr(180, 0, 0)
        alight = AmbientLight('alight')
        alight.setColor((0.5, 0.5, 0.5, 1))
        alnp = self.Manor.attachNewNode(alight)
        self.Manor.setLight(alnp)
        self.cameramodel = self.loader.loadModel(r'models/aidotupdater.glb')
        self.cameramodel.reparentTo(self.camera)
        self.wand = self.loader.loadModel("models/basic_wand.glb")
        self.wand.reparentTo(self.render)
        self.wand.setScale(.1, .1, .1)
        self.cameramodel.setPos(0, -18, 14)
        self.camera.setPos(0, -18, 14)
        # Create a collision traverser
        self.cTrav = CollisionTraverser()
        # Create a collision handler
        self.pusher = CollisionHandlerPusher()
        self.pusher.addInPattern("%fn-into-wall")
        for npc, collidername in zip(self.npcs.values(), self.colliderdict.values()):
                self.npcColliderpath = npc.attachNewNode(collidername)
        self.npcintocam = CollisionHandlerEvent()
        self.npcintocam.addInPattern('into-camera')
        # Create a collision node for the camera
        camera_collision_node = CollisionNode('camera')
        camera_collision_node.addSolid(CollisionSphere(0, 0, 0, 1.25))
        camera_collision_node_path = self.camera.attachNewNode(camera_collision_node)
        self.cTrav.addCollider(camera_collision_node_path, self.pusher) 
        self.pusher.addCollider(camera_collision_node_path, self.camera)
    def Dmgbynpc(self, task):
        print('damage')
        self.healthpoints-=1
        print(self.healthpoints)
    def createwalls(self):
        self.wall_collision_node = CollisionNode('wall')
        self.upstairdoor_collision_node = CollisionNode('upstairdoor')
        self.upstairdoor_collision_node.addSolid(CollisionBox(Point3(14, -9.5, 9), .5, 8, 4))
        self.upstairdoor_collision_node_path = self.render.attachNewNode(self.upstairdoor_collision_node)
        self.wall_collision_node.addSolid(CollisionBox(Point3(22, -6.5, 32), 19, .5, 27))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-23.5, -6.5, 32), 19, .5, 27))
        self.wall_collision_node.addSolid(CollisionBox(Point3(0, -6.5, 35), 10, .5, 25))
        self.wall_collision_node.addSolid(CollisionBox(Point3(0, -63, 30), 48, .5, 27))
        self.wall_collision_node.addSolid(CollisionBox(Point3(41, -35, 32), .5, 28, 27))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-43, -35, 32), .5, 28, 27))
        self.wall_collision_node.addSolid(CollisionPlane(Plane(Vec3(0, 0, 6.5), Point3(0, 0, 6.5))))
        self.wall_collision_node.addSolid(CollisionBox(Point3(0, 0, 0), 15, 7, 2))
        self.wall_collision_node.addSolid(CollisionBox(Point3(14, -32, 9), .3, 15, 4))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-17.5, -15, 9), 1.5, .3, 4))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-25, -15, 9), 1.7, .3, 4))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-15.75, -12.5, 9), .3, 6, 4))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-15.75, -34, 9), .3, 11.5, 4))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-15.75, -57.5, 9), .3, 5, 4))
        self.wall_collision_node.addSolid(CollisionBox(Point3(14, -56.5, 9), .3, 6, 4))
        self.wall_collision_node.addSolid(CollisionBox(Point3(13, -35, 9), 10, .3, 4))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-23, -35, 9), 19, .3, 4))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-25, -10, 9), .3, 5, 4))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-33,-41, 9), .3, 5.5, 4))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-33,-52.5, 9), .3, 2, 4))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-38,-55, 9), 5, .3, 4))
        self.wall_collision_node.addSolid(CollisionBox(Point3(23, -20.5, 9), .3, 14.5, 4))
        self.wall_collision_node.addSolid(CollisionBox(Point3(27, -25, 9), 3.5, .3, 4))
        self.wall_collision_node.addSolid(CollisionBox(Point3(37.5, -25, 9), 3.5, .3, 4))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-13, -9, 7), 1, 1, 1))
        self.wall_collision_node.addSolid(CollisionBox(Point3(8.5, -33, 6), 4.5, 1, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-10, -33, 6), 4.5, 1, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-17.5, -30, 6), 1, 4, 4))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-36, -34.25, 6), 6, 3.25, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-38.75, -25.5 , 6), 4, 1.25, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-40, -12 , 6), 2, 4, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-28, -11 , 6), 1, 1, 1))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-18, -11 , 6), 1, 1, 1))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-34.5, -41.4 , 6), 1, 3.6, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-42, -54 , 6), 1.5, 1.5, 1))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-25.75, -40, 6), .75, .5, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-22.5, -40, 6), .75, .5, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-25.75, -46, 6), .75, .5, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-22.5, -46, 6), .75, .5, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-24.25, -42.75, 6), 3.5, 1.5, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-18, -58, 6), 1, 5, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-42, -59, 6), 1, 3, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-11, -37, 6), 5, 1, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(12, -37, 6), 1, 1.5, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(11.25, -61.5, 6), 3.25, 1.5, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-13.5, -61, 6), 1, 1.5, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-1, -55, 6), 4.75, 2, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(6, -49, 6), 2, 1.5, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-7, -49, 6), 2, 1.5, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-.8, -49.25, 6), 2, 1.5, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-.75, -43, 6), 4.5, 1.75, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(15.8, -59.5, 6), .8, 2.95, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(23, -58.7, 6), 2.3, 4, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(39, -58.5, 6), 1.6, 4.2, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(39, -40.4, 6), 1.6, 13.155, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(17.75, -36, 6), 2.95, 1.5, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(25, -29.5, 6), 1.3, 2.95, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(24.5, -21, 6), .7, 1, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(26.1, -12.75, 6), 2.8, 1.4, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(24.5, -21, 6), .7, 1, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(39.5, -10, 6), 1, 1, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(39.5, -20.4, 6), 1, 2.5, .75))
        self.wall_collision_node.addSolid(CollisionPolygon(Point3(14.7, -15, 5), Point3(14.7, -32, 19.2), Point3(22.9, -32, 19.2), Point3(22.9, -15, 5)))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-16, -35, 14), 31, 28, 4.95))
        self.wall_collision_node.addSolid(CollisionBox(Point3(28, -47.5, 14), 13.5, 15.5, 4.95))
        self.wall_collision_node.addSolid(CollisionBox(Point3(32, -18.51, 14), 10, 13.5, 5))
        self.wall_collision_node.addSolid(CollisionPolygon(Point3(22, -29, 19.2), Point3(22, -33, 19.2), (50, -33, 19.2),Point3(50, -29, 19.2)))
        self.wall_collision_node.addSolid(CollisionPolygon(Point3(13.7, -32, 19.2), Point3(13.7, -67, 19.2), Point3(22.9, -67, 19.2), Point3(22.9, -32, 19.2)))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-10.8, -35, 21), 15.2, 5.9, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(6, -35, 21), 2, 4.5, .75))
        self.wall_collision_node.addSolid(CollisionBox(Point3(-28, -35, 21), 2, 4.5, .75))
        self.wall_collision_node_path = self.render.attachNewNode(self.wall_collision_node)
    def set(self):
        self.Aiworld = AIWorld(self.render)
        self.i = 0
        self.died = False
        self.waves = 1
        self.wavetext = OnscreenText(text="Wave: ", pos=(0,0.9), scale=0.1, fg=(1, 1, 1, 1), shadow=(0, 0, 0, .5))
        self.wavetext.setText("Wave: " + str(self.waves))
        #AI World updated
        taskMgr.add(self.Update,"Update")
        taskMgr.add(self.manaupdate,"manaupdate")
    def Update(self,task):
        camera_forward = self.camera.getQuat(self.render).getForward()
        camera_up = self.camera.getQuat(self.render).getUp()
        camera_right = self.camera.getQuat(self.render).getRight()
        camera_position = self.camera.getPos(self.render)
        self.tutorialine1.destroy()
        self.tutorialine2.destroy()
        self.tutorialine3.destroy()
        self.tutorialine4.destroy()
        self.tutorialine5.destroy()
        self.tutorialine6.destroy()
#        print(camera_position)
        # Calculate wand position: forward, slightly downward, and to the right
        wand_position = (
            camera_position +
            camera_forward * 1.5 -  # Forward by 1.0 units
            camera_up * 0.5 +       # Downward by 0.5 units
            camera_right * 0.4      # Rightward by 0.3 units
        )
        self.wand.setPos(wand_position)
        self.wand.setHpr(self.camera.getH(), 60, 10)
#        self.plnp.setHpr(self.camera.getHpr())
        if self.bossspawned == True:
            self.finalmodel.setPos(self.bossaimodel.getPos())
            self.finalmodel.setHpr(self.bossaimodel.getH(), 60, 10) 
            self.finalmodel.setZ(25)
            self.bosshealthbar["value"] = self.bosshealth
            if self.bosshealth <= 0 and self.won == False:
                winscreen = OnscreenImage(image = r"models/winscreen.jpg", pos = (0, 0, 0), scale = (2, 1, 1))
                self.bar.destroy()
                self.bosshealthbar.destroy()
                self.manabar.destroy()
                self.crosshair.destroy()
                self.bar = {"value": 0}
                self.bosshealthbar = {"value": 0}
                self.manabar = {"value": 0}
                self.won = True
        if self.onebutton != '**removed**' and self.haskey == True:
            self.onebutton.destroy()
            self.twobutton.destroy()
            self.threebutton.destroy()
            self.fourbutton.destroy()
            self.fivebutton.destroy()
            self.sixbutton.destroy()
            self.sevenbutton.destroy()
            self.eightbutton.destroy()
            self.ninebutton.destroy()
            self.zerobutton.destroy()
            self.clearbutton.destroy()
            self.enterbutton.destroy()
        # Set the wand's orientation to be vertical
        def update_npc_position(npc, aidot):
            npc.setH(aidot.getH())
            aidot.setZ(8)
            npc.setPos(aidot.getPos())
        for npc, aidot in zip(self.npcs.values(), self.aidotdict.values()):
            if not npc.isEmpty() and not aidot.isEmpty():
                update_npc_position(npc, aidot)
        # Separation logic to prevent NPC overlap
            separation_threshold = 3  # Minimum distance between NPCs
            repelling_force = .3  # Strength of the repelling force
            npc_positions = {name: npc.getPos(self.render) for name, npc in self.npcs.items() if not npc.isEmpty()}
            for name_a, pos_a in npc_positions.items():
                for name_b, pos_b in npc_positions.items():
                    if name_a != name_b:
                        distance = (pos_a - pos_b).length()
                        if distance < separation_threshold:
                        # Calculate repelling direction
                            direction = pos_a - pos_b
                            direction.normalize()
                        # Apply the repelling force
                            new_pos = pos_a + direction * repelling_force
                            self.npcs[name_a].setPos(new_pos)
        self.bar['value'] = self.healthpoints

        if self.healthpoints < 0 and self.died == False:
            self.death()
            self.died = True
        self.Aiworld.update()
        npcs_to_remove = []
        if self.npcs == {} and self.start == False:
            self.waves += 1
            self.wavetext.setText("Wave: " + str(self.waves))
            lowerwaves = (1,2,3,4)
            higherwaves = (5,6,7,8)
            if self.waves in lowerwaves:
                self.spawnateachdoor(num_npcs=2)
            if self.waves in higherwaves:
                self.spawnateachdoor(num_npcs=3)
        for key, health in self.npchealths.items():
            if health == 0:
                npcs_to_remove.append(key)
        for health in npcs_to_remove:
            self.npcs[health].removeNode()
            self.aidotdict[('aidot')+health[-1:]].removeNode()
            self.Aiworld.removeAiChar(('aichar')+health[-1:])
            self.Aicharbehaviorsdict['aibehavior'+health[-1:]].removeAi(('aibehavior')+health[-1:])
            del self.npcs[health]
            del self.aidotdict[('aidot')+health[-1:]]
            del self.Aichardict[('aichar')+health[-1:]]
            del self.Aicharbehaviorsdict[('aibehavior')+health[-1:]]
            del self.colliderdict[('collider')+health[-1:]]
            del self.npchealths[health]
        return Task.cont
    def __init__(self):
        super().__init__()
        taskMgr.add(self.tutorial,"tutorial")
        self.tutorialine1 = OnscreenText(text="Welcome to the game!", pos=(0,0.9), scale=0.08, fg=(1, 1, 1, 1), shadow=(0, 0, 0, .5))
        self.tutorialine2 = OnscreenText(text="W: Move Forward, S: Move Backward, A: Move Left, D: Move Right", pos=(0,0.7), scale=0.08, fg=(1, 1, 1, 1), shadow=(0, 0, 0, .5))
        self.tutorialine3 = OnscreenText(text="Click ghosts to make them disappear", pos=(0,0.5), scale=0.08, fg=(1, 1, 1, 1), shadow=(0, 0, 0, .5))
        self.tutorialine4 = OnscreenText(text="There is a safe in the house, find the code and put them into the safe", pos=(0,0.3), scale=0.07, fg=(1, 1, 1, 1), shadow=(0, 0, 0, .5))
        self.tutorialine5 = OnscreenText(text="There you will get a key, use it to open the big door to your left", pos=(0,0.1), scale=0.08, fg=(1, 1, 1, 1), shadow=(0, 0, 0, .5))
        self.tutorialine6 = OnscreenText(text="Hint: The code has a midas touch", pos=(0,-0.1), scale=0.08, fg=(1, 1, 1, 1), shadow=(0, 0, 0, .5))
        self.start = True
        self.loadmodels()
        self.safe_node = CollisionNode('safe')
        self.safe_node.addSolid(CollisionBox(Point3(-28, -11 , 4), 1, 1, 1))
        self.safe_node_path = self.render.attachNewNode(self.safe_node)
        self.accept('mouse1', self.click)
        self.accept('into-camera', self.Dmgbynpc)
        # Create a collision node for a walld
        MyApp.createwalls(self)
w = MyApp()
base.run()