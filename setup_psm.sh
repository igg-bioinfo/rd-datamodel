#//////////////////////////////////////////////////////////////////////////////
# FILE: setup.sh
# CREATED: 2022-12-01
# MODIFIED: 2022-12-01
# STATUS: stable
# PURPOSE: import URDM and assets into a new Molgenis instance
# COMMENTS: start by cloning this repository
#//////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Install molgenis commander
# See github repo for the latest installation instructions and release notes
# https://github.com/molgenis/molgenis-tools-commander/wiki/Installation-guide
# pip3 install --upgrade molgenis-commander

# run interactive config and set host (e.g., https://database.molgenis.org)
# mcmd config set host

# ~ 2 ~
# Import URDM and assets

# <!--- start: listEmxFiles --->
mcmd import -p dist/PerSAIDs.xlsx
mcmd import -p lookups/psm_lookups_MaleFemale.csv
mcmd import -p lookups/psm_lookups_AfricanArcticCaucasianCaucasianCaucasianCauca.csv
mcmd import -p lookups/psm_lookups_YesNoUnknown.csv
mcmd import -p lookups/psm_lookups_Degrees.csv
mcmd import -p lookups/psm_lookups_YesAsymptomaticCarrierNoUnknown.csv
mcmd import -p lookups/psm_lookups_YesNo.csv
mcmd import -p lookups/psm_lookups_AutosomicDominantRecessiveXLinkedUnknown.csv
mcmd import -p lookups/psm_lookups_NotdoneDoneWaitingforresponse.csv
mcmd import -p lookups/psm_lookups_CompleteGeneScreeningMostRelevantExonsMostRel.csv
mcmd import -p lookups/psm_lookups_TestNotInformativeTestInformativeTestNegative.csv
mcmd import -p lookups/psm_lookups_PresentNoPresentNotKnown.csv
mcmd import -p lookups/psm_lookups_NeverSometimesOrOftenAlwaysNotKnown.csv
mcmd import -p lookups/psm_lookups_NeverSometimesAlwaysNotKnown.csv
mcmd import -p lookups/psm_lookups_01Day2Days3Days4Days5Days6Days7Days8Days9Days.csv
mcmd import -p lookups/psm_lookups_1Day2Days3Days4Days5Days6Days7Days8Days9Days1.csv
mcmd import -p lookups/psm_lookups_MonolateralBilateralNotKnown.csv
mcmd import -p lookups/psm_lookups_RegularPeriodicIrregularNonPeriodicNotKnown.csv
mcmd import -p lookups/psm_lookups_YesNoNotApplicableNotKnown.csv
mcmd import -p lookups/psm_lookups_ContinuousRecurrentContinuousAndRecurrentComp.csv
mcmd import -p lookups/psm_lookups_NoMildSevereNotKnown.csv
mcmd import -p lookups/psm_lookups_SeriousNonSerious.csv
mcmd import -p lookups/psm_lookups_VerySevereSevereModerateNone.csv
mcmd import -p lookups/psm_lookups_FatalResolvedResolvedWithSequelaeImprovedPers.csv
mcmd import -p lookups/psm_lookups_PossibleProbableDefinite.csv
mcmd import -p lookups/psm_lookups_DoseReducedDoseIncreasedDrugInterruptedDrugDi.csv
mcmd import -p lookups/psm_lookups_NoYesUnknown.csv
mcmd import -p lookups/psm_lookups_NewOnsetWorseningUnknown.csv
mcmd import -p lookups/psm_lookups_Within24HoursLonger.csv
mcmd import -p lookups/psm_lookups_YesNoNotApplicable.csv
mcmd import -p lookups/psm_lookups_DoneNotDoneUnknown.csv
mcmd import -p lookups/psm_lookups_anatomicalSource.csv
mcmd import -p lookups/psm_lookups_ancestry.csv
mcmd import -p lookups/psm_lookups_biospecimenType.csv
mcmd import -p lookups/psm_lookups_country.csv
mcmd import -p lookups/psm_lookups_dataUseModifiers.csv
mcmd import -p lookups/psm_lookups_dataUsePermissions.csv
mcmd import -p lookups/psm_lookups_diagnosisConfirmationStatuses.csv
mcmd import -p lookups/psm_lookups_diseases.csv
mcmd import -p lookups/psm_lookups_fileStatus.csv
mcmd import -p lookups/psm_lookups_genomeAccessions.csv
mcmd import -p lookups/psm_lookups_genderIdentity.csv
mcmd import -p lookups/psm_lookups_genderAtBirth.csv
mcmd import -p lookups/psm_lookups_genotypicSex.csv
mcmd import -p lookups/psm_lookups_inclusionCriteria.csv
mcmd import -p lookups/psm_lookups_ngsKits.csv
mcmd import -p lookups/psm_lookups_pathologicalState.csv
mcmd import -p lookups/psm_lookups_phenotype.csv
mcmd import -p lookups/psm_lookups_samplingReason.csv
mcmd import -p lookups/psm_lookups_sequencingInstrumentModels.csv
mcmd import -p lookups/psm_lookups_sequencingMethods.csv
mcmd import -p lookups/psm_lookups_sequencingPlatform.csv
mcmd import -p lookups/psm_lookups_studyStatus.csv
mcmd import -p lookups/psm_lookups_subjectStatus.csv
# <!--- end: listEmxFiles --->
# mcmd delete -p psm # completing remove package
