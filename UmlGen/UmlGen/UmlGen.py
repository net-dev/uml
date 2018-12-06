from lxml import etree
import os
import logging
from logging_uml import get_uml_logger

# TODO own modules for loggin, parameters, xml parsing with functions
# TODO next step for objects 

# logger section
logger = get_uml_logger('uml_gen.log')

logger.info('Hello baby')

model_name = 'PortViewer'
xmi_file = 'd:/uml/source/port_viewer.xml'
base_path = 'd:/uml/develop'
gen_path = model_name + '/generated/interface/'
pat_path = 'pattern/'
# UML tool dependent constatns
model_tag = 'uml:Model'
# language depended constants
class_pattern = 'class.cs'
interface_pattern = 'interface.cs'
method_implementation_pattern = 'method_implementation.cs'
method_pattern = 'method_interface.cs'
derivation_key_word = ' : '

logger.info('Create projects structure')
if not os.listdir(base_path) :
    os.system("auto_sol.bat " + base_path)
if not os.path.exists(base_path + '/' + model_name) :
    os.system("auto_pro.bat " + base_path + " " + model_name)

# read text from file (file_tools)
xml = open(xmi_file, 'r').read()

# skip first line (string_tools)
xml = xml[xml.index("\n") + 1:]

# deseriazible from xml to dom (xml_tools)
root = etree.fromstring(xml)

# create namespaces dictionary (xml_tools)
ns = {'xmi': 'http://schema.omg.org/spec/XMI/2.1',
      'uml': "http://schema.omg.org/spec/UML/2.1"}

# create functions (xml_tools)
def name_with_ns(namespace, name, namespaces) :
    return '{' + namespaces[namespace] + '}' + name

def name_without_ns(name) :
    return name[name.index("}") + 1:]

logger.info('Sequence diagram processing')

for ll in root.xpath('//fragment[@xmi:type="uml:InteractionUse"]', namespaces = ns) :

    logger.info('Using sequence diagram ' + ll.get('name'))

    logger.info('Seqence diagram use - parameters')
    for p in root.xpath("//*[@base_InteractionUse='" + ll.get(name_with_ns('xmi', 'id', ns)) + "']", namespaces = ns) :

        class_name = p.attrib[name_without_ns(p.tag)]
        param_name = name_without_ns(p.tag)
        logger.info('Parameter ' + param_name + ' with value ' + class_name)

        logger.info('Generate in object ' + class_name)
        class_object = root.xpath("//packagedElement[@name='Class']/*/packagedElement[@name='" + class_name + "']", namespaces = ns)
        if len(class_object) > 0 :

            class_object_id = class_object[0].get(name_with_ns('xmi', 'id', ns))
            logger.info('Parameter class object id ' + class_object_id)

            # TODO extract method for generating class or interface
            logger.info('Determine namespace')
            name_space = ''
            parent_str = '/..'
            model_level = False
            while not model_level :
                parrent_object = root.xpath("//packagedElement[@name='Class']/*/packagedElement[@name='" + class_name + "']" + parent_str, namespaces = ns)
                model_level = parrent_object[0].get(name_with_ns('xmi', 'type', ns)) == model_tag
                if not model_level :
                    name_space_level = parrent_object[0].get('name')
                    if name_space_level.upper() != 'CLASS' :
                        if name_space != '' : 
                            name_space = '.' + name_space
                        name_space = name_space_level + name_space
                    parent_str =  parent_str + '/..'
            logger.info('Namespace ' + name_space)

            logger.info('Determine ascesor and create properties, operations and eventually interface')
            ascesor = class_object[0].get('classifier') 
            if ascesor != None :
                ascesor_name = root.xpath("//packagedElement[@xmi:id='" + ascesor + "']", namespaces = ns)[0].get('name')
                is_interface = root.xpath("//*[@base_Class='" + ascesor + "']", namespaces = ns)
            else :
                ascesor_name = ''
                is_interface = None

            class_interfaces_list = ''

            logger.info('Read patterns')
            pattern = open(pat_path + class_pattern, 'r').read()
            pattern_method = open(pat_path + method_implementation_pattern, 'r').read()

            logger.info('Generate class interfaces')
            interfaces_list = ''
            interfaces_for_object = root.xpath("//packagedElement[@name='Class']/*/packagedElement[@xmi:type='uml:Realization' and @client='" + class_object_id + "']", namespaces = ns)
            for i in interfaces_for_object :
                interface_method_list = ''
                implementation_method_list = ''
                interface_id = i.get('supplier')
                logger.info('Interface with id ' + interface_id)
                interface_object = root.xpath("//packagedElement[@xmi:id='" + interface_id + "']", namespaces = ns)[0]
                interface_name = interface_object.get('name')
                if interfaces_list != '' :
                    interfaces_list = interfaces_list + ', '
                interfaces_list = interfaces_list + interface_name
                logger.info('Interface with name ' + interface_name)
                for m in root.xpath("//packagedElement[@xmi:id='" + interface_id + "']/ownedOperation", namespaces = ns) :
                    pattern_method = pattern_method.replace(
                        '[method_result]', 'string').replace(
                        '[method_parameters]', '').replace(
                        '[method_logic]', '').replace(
                        '[method_name]', m.get('name'))
                    if interface_method_list != '' :
                        interface_method_list = interface_method_list + '\n'
                    interface_method_list = interface_method_list + pattern_method
            logger.info('Fill pattern')
            if ascesor_name != '' :
                class_interfaces_list = ascesor_name
            if ascesor_name != '' :
                if interfaces_list != '' :
                    class_interfaces_list = class_interfaces_list + ', ' + interfaces_list
            if ascesor_name != '' or interfaces_list != '' :
                class_interfaces_list = derivation_key_word + interfaces_list

            # TODO case on class/interface contition
            implementation_method_list = interface_method_list
            pattern = pattern.replace(
                '[class_name]', class_name).replace(
                '[name_space]', name_space).replace(
                '[ascesor_interface]', class_interfaces_list).replace(
                '[methods_interface]', interface_method_list).replace(
                '[method_implementation]', implementation_method_list)

            logger.info('Generate code')

            logger.info('Path for generate class object')
            dir_name_space = name_space.replace('.', '/') + '/'
            # remove model at beginning
            dir_name_space = dir_name_space[dir_name_space.index("/") + 1:]

            logger.info('Create directory')
            if not os.path.exists(base_path + '/' + gen_path + dir_name_space) :
                os.makedirs(base_path + '/' + gen_path + dir_name_space)

            logger.info('Create class file')
            gen = open(base_path + '/' + gen_path + dir_name_space + class_name + '.cs', 'w+')

            logger.info('Write class file')
            gen.write(pattern)

            logger.info('Finalization')
            gen.close()
