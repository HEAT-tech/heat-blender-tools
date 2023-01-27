import bpy


class APISearchAnimationsOperator(bpy.types.Operator):
    bl_idname = "heat.api_search_animations"
    bl_label = "Search Heat animations"

    def execute(self, context):
        context.scene.heat_animation_results_list.clear()
        movements = [
            {
                "description": "T69h Test 2 Json File",
                "downloadUrl": "https://arbztjwhu7.execute-api.us-west-1.amazonaws.com/dev/v1/movements/9afe4ae5-5494-4806-ab1f-b154217a88d3/download",
                "movementID": "9afe4ae5-5494-4806-ab1f-b154217a88d3",
                "name": "T69h Test 2",
                "url": "https://arbztjwhu7.execute-api.us-west-1.amazonaws.com/dev/v1/movements/9afe4ae5-5494-4806-ab1f-b154217a88d3"
            },
            {
                "description": "T69h Test 3 Json File",
                "downloadUrl": "https://arbztjwhu7.execute-api.us-west-1.amazonaws.com/dev/v1/movements/852e7d14-7009-408f-becb-c8e909952c8a/download",
                "movementID": "852e7d14-7009-408f-becb-c8e909952c8a",
                "name": "T69h Test 3",
                "url": "https://arbztjwhu7.execute-api.us-west-1.amazonaws.com/dev/v1/movements/852e7d14-7009-408f-becb-c8e909952c8a"
            },
            {
                "description": "T69h Test 4 Json File",
                "downloadUrl": "https://arbztjwhu7.execute-api.us-west-1.amazonaws.com/dev/v1/movements/902ed606-8ae6-4a1f-8814-8bfd635bcd4a/download",
                "movementID": "902ed606-8ae6-4a1f-8814-8bfd635bcd4a",
                "name": "T69h Test 4",
                "url": "https://arbztjwhu7.execute-api.us-west-1.amazonaws.com/dev/v1/movements/902ed606-8ae6-4a1f-8814-8bfd635bcd4a"
            }
        ]

        movements_list = []
        for movement in movements:
            new_movement = context.scene.heat_animation_results_list.add()
            new_movement.name = movement['name']


        return {'FINISHED'}

    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)
