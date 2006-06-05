/**
 * \file    UniqueSpeciesTypesInCompartment.cpp
 * \brief   Ensures unique variables assigned by rules and events
 * \author  Sarah Keating
 *
 * $Id$
 * $Source$
 */
/* Copyright 2005 California Institute of Technology and Japan Science and
 * Technology Corporation.
 *
 * This library is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation.  A copy of the license agreement is
 * provided in the file named "LICENSE.txt" included with this software
 * distribution.  It is also available online at
 * http://sbml.org/software/libsbml/license.html
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this library; if not, write to the Free Software Foundation,
 * Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA.
 */


#include <string>

#include <sbml/Model.h>
#include <sbml/Rule.h>
#include <sbml/Reaction.h>
#include <sbml/Species.h>

#include "UniqueSpeciesTypesInCompartment.h"
#include "IdList.h"


using namespace std;




/**
 * Creates a new Constraint with the given constraint id.
 */
UniqueSpeciesTypesInCompartment::UniqueSpeciesTypesInCompartment (unsigned int id, Validator& v) :
  TConstraint<Model>(id, v)
{
}


/**
 * Destroys this Constraint.
 */
UniqueSpeciesTypesInCompartment::~UniqueSpeciesTypesInCompartment ()
{
}


/**
  * Checks that any species with boundary condition false
  * is not set by reaction and rules
  */
void
UniqueSpeciesTypesInCompartment::check_ (const Model& m, const Model& object)
{
  unsigned int n, ns;

  for (n = 0; n < m.getNumCompartments(); n++)
  {
    const string & id = m.getCompartment(n)->getId();

    /* create List of species in this compartment */
    for (ns = 0; ns < m.getNumSpecies(); ns++)
    {
      if (!strcmp(m.getSpecies(ns)->getCompartment().c_str(), id.c_str()))
      {
        mSpecies.append(m.getSpecies(ns)->getId());
      }
    } 

    /* loop thru the list of Species in the compartment and check that
       no speciesTypes are same */
    for (IdList::const_iterator the_iterator = mSpecies.begin();
      the_iterator != mSpecies.end(); the_iterator++)
    {
      if (m.getSpecies(*the_iterator)->isSetSpeciesType()) 
      {
        const string & type = m.getSpecies(*the_iterator)->getSpeciesType();

        if (mSpeciesTypes.contains(type))
        {
          logConflict(*m.getSpecies(*the_iterator), *m.getCompartment(n));
        }
        else
        {
          mSpeciesTypes.append(type);
        }
      }
    }

    mSpecies.clear();
    mSpeciesTypes.clear();

  }
}

/**
  * Logs a message about species with boundary condition false
  * being set by reaction and rules
  */
void
UniqueSpeciesTypesInCompartment::logConflict (const Species& s, const Compartment& c)
{
  msg =
    "A Compartment cannot contain more than one species with the same "
    "SpeciesType. "
    "The compartment '";

  msg += c.getId();
  msg += "' contains more than one species withSpeciesType '";
  msg += s.getSpeciesType();
  msg += "'.";

  
  logFailure(s);
}